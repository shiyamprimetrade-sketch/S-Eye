"""Source-grid overlays; amber boxes remain unverified geometric hypotheses."""
import math
from PIL import ImageDraw
from seye.detection.metrics import valid_box
from seye.image.ingestion import load_image
from seye.integration.observations import observe_image
from seye.local.workspace import open_workspace,publish


def render(image,regions):
    if not isinstance(regions,list) or len(regions)>128:raise ValueError('At most 128 explicit regions supported')
    boxes=[]
    for region in regions:
        if not isinstance(region,dict):raise ValueError('Region object required')
        box=region.get('box');valid_box(box)
        if not 0<=box[0]<box[2]<=image.width or not 0<=box[1]<box[3]<=image.height:raise ValueError('Overlay box outside source grid')
        boxes.append(list(box))
    overlay=image.convert('RGB').copy();draw=ImageDraw.Draw(overlay)
    for index,box in enumerate(boxes,1):
        left,top=math.floor(box[0]),math.floor(box[1]);right,bottom=math.ceil(box[2])-1,math.ceil(box[3])-1
        draw.rectangle((left,top,right,bottom),outline=(255,170,20),width=2)
        draw.text((left,max(0,top-12)),f'R{index}',fill=(180,80,0))
    return overlay


def overlay_workspace(workspace,destination,allowed_root):
    root,data,digest=open_workspace(workspace,allowed_root)
    def build(stage):
        rows=[]
        for item in data['items']:
            path=root/item['path'];observed=observe_image(path,item['source']['sha256'])
            image,source=load_image(path,max_pixels=4_000_000)
            if source['sha256']!=item['source']['sha256']:raise ValueError('Source changed before overlay')
            regions=observed['observation']['region_proposals']['regions'];name=item['id']+'.png'
            with (stage/name).open('xb') as stream:render(image,regions).save(stream,format='PNG')
            rows.append({'id':item['id'],'overlay':name,'source_sha256':source['sha256'],'source_size':source['size'],
                         'regions':[{'box':r['box']} for r in regions],'observation_sha256':observed['identity']['observation_sha256']})
        return {'format':'seye-overlay-set-v1','schema_version':1,'workspace_sha256':digest,'items':rows,
                'scope':'amber source-coordinate geometric hypotheses; no semantic identity or clickability'}
    return publish(destination,allowed_root,build)
