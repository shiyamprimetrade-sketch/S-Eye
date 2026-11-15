"""Offline HTML/JSON evidence reports; training labels are escaped, not instructions."""
import base64,html,io,json
from seye.core.storage import atomic_json,checksum,canonical
from seye.image.ingestion import load_image
from seye.integration.observations import observe_image
from seye.local.workspace import open_workspace,publish,inside


def document(title,body,script=None):
    policy="default-src 'none'; img-src data: blob:; style-src 'unsafe-inline'; connect-src 'none'"
    if script is not None:policy+="; script-src 'unsafe-inline'"
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="'+html.escape(policy,quote=True)+'"><title>'+html.escape(title)+'</title>'
            '<style>body{margin:0;background:#f1f5f9;color:#172033;font:16px system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:24px}h1{line-height:1.15}p{line-height:1.5}.badge{color:#92400e;background:#fef3c7;padding:6px 10px;border-radius:8px}article{background:white;padding:20px;border-radius:14px;margin:16px 0;box-shadow:0 2px 12px #1720330c}code,pre{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%;border:1px solid #cbd5e1}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:9px;border-bottom:1px solid #e2e8f0;overflow-wrap:anywhere}button,select{font:inherit;padding:10px;border-radius:8px;border:1px solid #94a3b8;background:white}button{cursor:pointer}canvas{max-width:100%;height:auto;touch-action:none;border:1px solid #94a3b8}small{color:#475569}</style>'
            '<main><h1>'+html.escape(title)+'</h1>'+body+'</main>'+
            ('<script>'+script+'</script>' if script is not None else '')+'</html>')


def preview(image,maximum=(320,240)):
    image=image.convert('RGB').copy();image.thumbnail(maximum)
    stream=io.BytesIO();image.save(stream,format='PNG')
    return 'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()


def prediction_summary(prediction):
    if prediction is None:return {'status':'not_requested','label':None,'confidence_probability':None}
    selection=prediction['selection']
    if not isinstance(selection.get('label'),str) or not 1<=len(selection['label'])<=128:raise ValueError('Bounded supplied training label required')
    return {'status':'model_label' if selection['accepted'] else 'rejected_or_ambiguous','label':selection['label'],
            'reason':selection['reason'],'distance':selection['nearest_distance'],'radius':selection['rejection_radius'],
            'confidence_probability':None,'scope':'supplied training-category decision, not verified semantic recognition'}


def build_report(workspace,destination,allowed_root,model_path=None):
    root,data,digest=open_workspace(workspace,allowed_root);model=None;model_sha=None
    if model_path is not None:
        from seye.learning.packet_prototypes import load
        model=load(inside(model_path,allowed_root));model_sha=checksum(model)
        if any(len(name)>128 for name in model['classes']):raise ValueError('Model labels exceed report bounds')
    def build(stage):
        rows=[];cards=[]
        for item in data['items']:
            path=root/item['path'];source=item['source'];observed=observe_image(path,source['sha256'])
            image,current=load_image(path,max_pixels=4_000_000)
            if current['sha256']!=source['sha256']:raise ValueError('Report source changed')
            regions=observed['observation']['region_proposals']['regions'];prediction=None;error=None
            if model is not None:
                try:
                    from seye.recognition.pipeline import FeaturePipeline
                    from seye.recognition.explanation import explain
                    schema=model['prototypes'][model['classes'][0]]['schema']
                    packet=FeaturePipeline().extract(image,[p['name'] for p in schema['components']]);prediction=explain(model,packet)
                    canonical(prediction)
                except (ValueError,KeyError,TypeError,OverflowError) as caught:error=str(caught)
            decision={'status':'failed','label':None,'error':error,'confidence_probability':None} if error else prediction_summary(prediction)
            row={'id':item['id'],'source_sha256':source['sha256'],'source_size':source['size'],'source_kind':item['source_kind'],
                 'region_count':len(regions),'boxes':[r['box'] for r in regions],'decision':decision}
            rows.append(row)
            cards.append('<article><h2>'+html.escape(item['id'])+'</h2><p>'+html.escape(str(item.get('source_filename','')))+
                         '</p><img alt="Captured image preview" src="'+preview(image)+'"><p><strong>'+str(len(regions))+
                         ' geometric hypotheses</strong> · decision: '+html.escape(decision['status'])+'</p><p>Training label: '+html.escape(str(decision.get('label')))+
                         '</p><small>Source SHA-256</small><code>'+source['sha256']+'</code><pre>'+html.escape(json.dumps(row,indent=2))+'</pre></article>')
        report={'format':'seye-local-analysis-v1','schema_version':1,'workspace_sha256':digest,'model_sha256':model_sha,'items':rows,
                'semantic_recognition_validated':False,'scope':'generated geometric proposals and optional supplied prototype decisions; no calibrated probabilities or accuracy without labels'}
        if len(canonical(report))>8*1024*1024:raise ValueError('Local report exceeds 8 MiB')
        atomic_json(stage/'report.json',report)
        content=document('S-Eye · visual evidence','<p class="badge">Experimental · hypotheses, not verified objects</p><p>Source-linked local evidence. No OCR or clickability inference.</p>'+''.join(cards))
        if len(content.encode('utf-8'))>16*1024*1024:raise ValueError('Offline HTML report exceeds 16 MiB')
        (stage/'report.html').write_text(content,encoding='utf-8')
        return {'format':'seye-local-report-bundle-v1','schema_version':1,'report_sha256':checksum(report),'workspace_sha256':digest,
                'files':['report.json','report.html'],'items':len(rows)}
    return publish(destination,allowed_root,build)
