"""Bounded, exclusive local bundles with a final checksummed manifest marker."""
import hashlib,os,re,shutil,tempfile
from pathlib import Path
from seye.core.storage import atomic_json,checksum,read_json
from seye.image.ingestion import load_image
from seye.integration.service import Permissions


def inside(path,root):
    try:
        # Python 3.13 non-strict resolution can retain symlink loops. Probe
        # strictly first while still permitting a new, absent output path.
        try:target=Path(path).resolve(strict=True)
        except FileNotFoundError:target=Path(path).resolve()
        allowed=Path(root).resolve(strict=True)
    except (OSError,RuntimeError) as error:raise PermissionError('Workflow path could not be resolved') from error
    if not target.is_relative_to(allowed):raise PermissionError('Workflow path outside explicit allowed root')
    return target


def publish(destination,allowed_root,builder):
    """Build privately, publish exclusively, manifest last; no directory overwrite.

    Readers require the completion manifest. This is not an atomic directory
    rename or a power-loss transaction; abrupt termination may leave a partial.
    """
    requested=Path(destination)
    if requested.is_symlink():raise FileExistsError('Choose a new output directory, not an existing symlink')
    destination=inside(destination,allowed_root)
    if destination.exists() or destination.is_symlink():raise FileExistsError('Choose a new output directory')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.seye-local-',dir=destination.parent) as name:
        stage=Path(name);manifest=builder(stage)
        atomic_json(stage/'manifest.json',{'payload':manifest,'sha256':checksum(manifest)})
        destination.mkdir(mode=0o700,exist_ok=False)
        try:
            files=sorted(p for p in stage.rglob('*') if p.is_file() and p.name!='manifest.json')+[stage/'manifest.json']
            for path in files:
                target=destination/path.relative_to(stage);target.parent.mkdir(parents=True,exist_ok=True)
                os.link(path,target)
        except BaseException:
            shutil.rmtree(destination)
            raise
    return {'directory':str(destination),'manifest_sha256':checksum(manifest),'format':manifest['format']}


def ingest(paths,destination,allowed_root,source_kind='screenshot'):
    if not isinstance(paths,(list,tuple)) or not 1<=len(paths)<=32:raise ValueError('Choose 1..32 explicit source images')
    if source_kind not in ('screenshot','photograph','synthetic'):raise ValueError('Explicit supported source kind required')
    permissions=Permissions((allowed_root,));sources=[permissions.require(path) for path in paths]
    def build(stage):
        items=[];total_bytes=total_pixels=0;(stage/'images').mkdir()
        for index,path in enumerate(sources,1):
            image,source=load_image(path,max_pixels=min(4_000_000,32_000_000-total_pixels),
                                    max_bytes=min(32*1024*1024,64*1024*1024-total_bytes))
            with path.open('rb') as stream:raw=stream.read(32*1024*1024+1)
            if len(raw)>32*1024*1024 or hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Source changed during import')
            total_bytes+=len(raw);total_pixels+=image.width*image.height
            relative=f'images/{index:04d}'+path.suffix.lower()
            with (stage/relative).open('xb') as stream:stream.write(raw)
            items.append({'id':f'image-{index:04d}','path':relative,'source_filename':path.name,'source_kind':source_kind,
                          'source':source,'annotation_status':'unlabelled'})
        return {'format':'seye-local-workspace-v1','schema_version':1,'items':items,'encoded_bytes':total_bytes,
                'decoded_pixels':total_pixels,'scope':'verified source-file snapshots; no labels or recognition accuracy inferred'}
    return publish(destination,allowed_root,build)


def open_workspace(path,allowed_root):
    root=inside(path,allowed_root);envelope=read_json(root/'manifest.json',max_bytes=256*1024);data=envelope.get('payload')
    if not isinstance(data,dict) or envelope.get('sha256')!=checksum(data) or data.get('format')!='seye-local-workspace-v1' or type(data.get('schema_version')) is not int or data['schema_version']!=1:raise ValueError('Workspace completion manifest invalid')
    items=data.get('items');seen=set();total_bytes=total_pixels=0
    if not isinstance(items,list) or not 1<=len(items)<=32:raise ValueError('Invalid workspace image count')
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not re.fullmatch('image-[0-9]{4}',item['id']) or item['id'] in seen:raise ValueError('Unique workspace image ID required')
        seen.add(item['id']);relative=item.get('path')
        if not isinstance(relative,str) or re.fullmatch(r'images/[0-9]{4}\.(png|jpg|jpeg)',relative) is None:raise ValueError('Workspace path is not a generated image path')
        if item.get('source_kind') not in ('screenshot','photograph','synthetic') or item.get('annotation_status')!='unlabelled':raise ValueError('Invalid workspace source declaration')
        image,source=load_image(root/relative,allowed_root=root,max_pixels=4_000_000)
        expected=item.get('source',{})
        if not isinstance(expected,dict) or not isinstance(item.get('source_filename'),str) or not 1<=len(item['source_filename'])<=255:raise ValueError('Bounded source filename and metadata required')
        size=expected.get('size')
        if not isinstance(size,list) or len(size)!=2 or any(type(v) is not int or v<=0 for v in size):raise ValueError('Integer source grid required')
        if type(expected.get('bytes')) is not int or expected['bytes']<=0:raise ValueError('Integer encoded source bytes required')
        if any(source[k]!=expected.get(k) for k in ('sha256','bytes','size')):raise ValueError('Workspace source identity mismatch')
        total_bytes+=source['bytes'];total_pixels+=image.width*image.height
    if total_bytes>64*1024*1024 or total_pixels>32_000_000 or total_bytes!=data.get('encoded_bytes') or total_pixels!=data.get('decoded_pixels'):raise ValueError('Workspace resource accounting mismatch')
    return root,data,envelope['sha256']
