"""Renderer-oracle scene changes and real-input execution kept separate."""
from collections import Counter
from PIL import Image,ImageDraw
from seye.interface.localization import localize
from seye.memory.identity import pixel_identity
from seye.scenes.changes import changes
from seye.detection.metrics import detection_metrics


def fixtures():
    a=[20,16,60,40];b=[110,60,150,84]
    specifications=[('stable',[a],[a],{'stable':1}),('moved',[a],[[28,20,68,44]],{'moved':1}),
                    ('resized',[a],[[20,16,68,44]],{'resized':1}),('missing',[a,b],[a],{'stable':1,'missing':1}),
                    ('appeared',[a],[a,b],{'stable':1,'appeared':1}),
                    ('nested',[[12,8,160,98],[30,28,70,52]],[[12,8,160,98],[38,28,78,52]],{'stable':1,'moved':1}),
                    ('overlap',[a,b],[[20,16,70,48],[50,32,100,64]],{'resized':1,'missing':1,'appeared':1}),
                    ('viewport',[a],[a],{})]
    for theme in ('dark','light'):
        for scale in (1,1.5):
            for state,before,after,expected in specifications:
                images=[];truth=[]
                for index,boxes in enumerate((before,after)):
                    factor=scale*(2 if state=='viewport' and index==1 else 1);size=(round(240*factor),round(160*factor))
                    image=Image.new('RGB',size,(20,20,20) if theme=='dark' else (230,230,230));draw=ImageDraw.Draw(image);rows=[]
                    for j,box in enumerate(boxes):
                        box=[round(v*factor) for v in box];rows.append({'class':'interface_region','box':box});color=(220,220,220) if theme=='dark' else (40,40,40)
                        if state=='nested' and j==0:draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),outline=color,width=2)
                        else:draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=color)
                    images.append(image);truth.append(rows)
                yield {'id':f'{theme}-{scale}-{state}','theme':theme,'scale':scale,'state':state,'expected_events':expected,
                       'expected_comparable':state!='viewport','truth':truth},images


def run():
    cases=[];totals={'tp':0,'fp':0,'fn':0};event_matches=0;by_state={}
    for metadata,images in fixtures():
        frames=[];scores=[]
        for image,truth in zip(images,metadata['truth']):
            report=localize(image);rows=[{'class':r['class'],'box':r['box']} for r in report['regions']]
            frames.append({'objects':rows,'source_size':list(image.size),'source_sha256':pixel_identity(image),'complete':report['complete']})
            metrics=detection_metrics(truth,rows)
            for key in totals:totals[key]+=metrics[key]
            scores.append(metrics)
        report=changes(*frames);actual=Counter(e['kind'] for e in report['events'])
        if report['comparable']:actual.update({'missing':len(report['missing']),'appeared':len(report['appeared'])})
        actual={key:value for key,value in actual.items() if value};good=report['comparable']==metadata['expected_comparable'] and actual==metadata['expected_events'];event_matches+=good
        group=by_state.setdefault(metadata['state'],{'pairs':0,'event_matches':0});group['pairs']+=1;group['event_matches']+=good
        cases.append(dict(metadata,actual_events=actual,event_match=good,localization=scores,source_pixel_hashes=[f['source_sha256'] for f in frames],comparison=report))
    return {'pairs':len(cases),'frames':2*len(cases),'event_count_contract_matches':event_matches,'localization':totals,'by_state':by_state,'cases':cases,
            'representative_application_validation':False,
            'limitations':['Shared generated rectangles and automatic renderer oracles, not representative UI/photograph labels.',
                           'Overlap/segmentation failures remain in all denominators.','Event scoring is geometric correspondence, not semantic object identity.']}
