"""Offline source-coordinate drawing of unscored annotation drafts."""
import json
from seye.core.storage import atomic_json,checksum,canonical
from seye.detection.metrics import valid_box
from seye.image.ingestion import load_image
from seye.local.workspace import open_workspace,publish
from seye.local.reports import document,preview

CLASSES=('interface_region','quadrilateral','triangle','circle','unknown')


def new_draft(data,digest):
    return {'format':'seye-annotation-draft-v1','schema_version':1,'workspace_sha256':digest,'template_unscored':True,
            'images':[{'id':r['id'],'path':r['path'],'sha256':r['source']['sha256'],'source_size':r['source']['size'],
                       'source_kind':r['source_kind'],'annotation_status':'draft','annotation_origin':'caller_drawn',
                       'capture_group':'unassigned','instances':[]} for r in data['items']]}


def validate_draft(draft,data,digest):
    if not isinstance(draft,dict) or draft.get('format')!='seye-annotation-draft-v1' or type(draft.get('schema_version')) is not int or draft['schema_version']!=1 or draft.get('workspace_sha256')!=digest or draft.get('template_unscored') is not True:raise ValueError('Source-bound unscored draft required')
    rows=draft.get('images')
    if not isinstance(rows,list) or len(rows)!=len(data['items']):raise ValueError('Draft source inventory mismatch')
    for row,source in zip(rows,data['items']):
        if not isinstance(row,dict) or row.get('id')!=source['id'] or row.get('path')!=source['path'] or row.get('sha256')!=source['source']['sha256'] or row.get('source_size')!=source['source']['size'] or row.get('source_kind')!=source['source_kind']:raise ValueError('Draft source identity mismatch')
        if row.get('annotation_status')!='draft' or row.get('annotation_origin')!='caller_drawn':raise ValueError('Editor never asserts generator truth or human-reviewed status')
        if not isinstance(row.get('capture_group'),str) or not 1<=len(row['capture_group'])<=128:raise ValueError('Bounded capture group declaration required')
        instances=row.get('instances')
        if not isinstance(instances,list) or len(instances)>128:raise ValueError('At most 128 draft boxes per image')
        ids=set();width,height=row['source_size']
        for instance in instances:
            if not isinstance(instance,dict) or not isinstance(instance.get('id'),str) or not 1<=len(instance['id'])<=64 or instance['id'] in ids or instance.get('class') not in CLASSES:raise ValueError('Unique draft IDs and supported geometric labels required')
            ids.add(instance['id']);box=instance.get('box');valid_box(box)
            if not 0<=box[0]<box[2]<=width or not 0<=box[1]<box[3]<=height:raise ValueError('Draft box outside source grid')
    if len(canonical(draft))>2*1024*1024:raise ValueError('Draft exceeds 2 MiB')
    return {'images':len(rows),'instances':sum(len(r['instances']) for r in rows),'unscored':True}


EDITOR_SCRIPT=r'''
const draft=JSON.parse(JSON.stringify(INITIAL));
const choose=document.getElementById('image'), label=document.getElementById('class');
const canvas=document.getElementById('canvas'), ctx=canvas.getContext('2d'), status=document.getElementById('status');
let current=0, bitmap=new Image(), start=null, pending=null, ready=false;
for(let i=0;i<draft.images.length;i++){const o=document.createElement('option');o.value=i;o.textContent=draft.images[i].id;choose.appendChild(o);}
for(const name of LABELS){const o=document.createElement('option');o.value=name;o.textContent=name;label.appendChild(o);}
function point(event){const r=canvas.getBoundingClientRect(), s=draft.images[current].source_size;
 return [Math.max(0,Math.min(s[0],(event.clientX-r.left-canvas.clientLeft)/(r.width-2*canvas.clientLeft)*s[0])),
         Math.max(0,Math.min(s[1],(event.clientY-r.top-canvas.clientTop)/(r.height-2*canvas.clientTop)*s[1]))];}
function redraw(){if(!ready)return;ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);
 const row=draft.images[current], sx=canvas.width/row.source_size[0],sy=canvas.height/row.source_size[1];
 ctx.strokeStyle='#f59e0b';ctx.lineWidth=2;ctx.fillStyle='#92400e';
 for(const item of row.instances){const b=item.box;ctx.strokeRect(b[0]*sx,b[1]*sy,(b[2]-b[0])*sx,(b[3]-b[1])*sy);ctx.fillText(item.class+' (draft)',b[0]*sx,Math.max(12,b[1]*sy-4));}
 if(start&&pending){ctx.strokeStyle='#2563eb';ctx.strokeRect(start[0]*sx,start[1]*sy,(pending[0]-start[0])*sx,(pending[1]-start[1])*sy);}
 status.textContent=row.instances.length+' draft boxes · source '+row.source_size.join(' × ')+' · '+row.sha256;
}
function select(){current=Number(choose.value);start=pending=null;ready=false;status.textContent='Loading preview · draft remains unscored';bitmap=new Image();bitmap.onload=()=>{canvas.width=bitmap.naturalWidth;canvas.height=bitmap.naturalHeight;ready=true;redraw();};bitmap.onerror=()=>{status.textContent='Preview could not load · draft remains unscored';};bitmap.src=PREVIEWS[current];}
choose.addEventListener('change',select);
canvas.addEventListener('pointerdown',e=>{if(!ready)return;start=point(e);pending=start;canvas.setPointerCapture(e.pointerId);redraw();});
canvas.addEventListener('pointermove',e=>{if(start){pending=point(e);redraw();}});
canvas.addEventListener('pointerup',e=>{if(!ready||!start)return;const end=point(e),b=[Math.min(start[0],end[0]),Math.min(start[1],end[1]),Math.max(start[0],end[0]),Math.max(start[1],end[1])].map(v=>Math.round(v*100)/100);
 const row=draft.images[current];if(b.every(Number.isFinite)&&b[2]-b[0]>=1&&b[3]-b[1]>=1&&row.instances.length<128)row.instances.push({id:'box-'+(row.instances.length+1),class:label.value,box:b});start=pending=null;redraw();});
canvas.addEventListener('pointercancel',()=>{start=pending=null;redraw();});
document.getElementById('undo').addEventListener('click',()=>{if(!ready)return;draft.images[current].instances.pop();redraw();});
document.getElementById('download').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(draft,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='seye-annotation-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
select();
'''


def safe_script_json(value):return json.dumps(value,ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')


def build_editor(workspace,destination,allowed_root,draft=None):
    root,data,digest=open_workspace(workspace,allowed_root)
    draft=new_draft(data,digest) if draft is None else draft
    validate_draft(draft,data,digest);previews=[]
    for row in data['items']:
        image,source=load_image(root/row['path'],max_pixels=4_000_000)
        if source['sha256']!=row['source']['sha256']:raise ValueError('Editor source changed')
        previews.append(preview(image,(800,800)))
    script='const INITIAL='+safe_script_json(draft)+';const PREVIEWS='+safe_script_json(previews)+';const LABELS='+safe_script_json(CLASSES)+';'+EDITOR_SCRIPT
    body='<p class="badge">Draft · unscored · never automatically marked reviewed</p><p>Drag a box over the preview. Coordinates are mapped to the original source grid. Labels are caller assertions; empty drafts do not assert a negative image.</p><article><label>Image <select id="image" aria-label="Image"></select></label> <label>Class <select id="class" aria-label="Class"></select></label> <button id="undo">Undo last box</button> <button id="download">Download draft JSON</button><p id="status" style="overflow-wrap:anywhere" aria-live="polite"></p><canvas id="canvas" aria-label="Source annotation canvas" style="box-sizing:border-box;display:block"></canvas></article>'
    content=document('S-Eye · annotation draft',body,script)
    if len(content.encode('utf-8'))>16*1024*1024:raise ValueError('Standalone editor exceeds 16 MiB')
    def build(stage):
        atomic_json(stage/'draft.json',draft);(stage/'annotate.html').write_text(content,encoding='utf-8')
        return {'format':'seye-annotation-editor-v1','schema_version':1,'workspace_sha256':digest,'draft_sha256':checksum(draft),
                'files':['draft.json','annotate.html'],'scope':'scaled-preview geometric draft editing; no validated labels, source edits or network calls'}
    return publish(destination,allowed_root,build)
