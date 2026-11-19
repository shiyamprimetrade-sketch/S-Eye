#!/usr/bin/env python3
"""Actual generated MPEG4 -> decoder -> segmentation -> conservative tracking."""
from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.video.resources import run_decoder,hash_file
from seye.video.interface import observe_video
from seye.video.evaluation import evaluate


def run():
    cases=[]
    with tempfile.TemporaryDirectory(prefix='seye_temporal_encode_') as directory:
        root=Path(directory)
        for kind in ('steady','short_gap','overlap'):
            folder=root/kind;folder.mkdir();truth=[]
            for i in range(8):
                x1,x2=20+4*i,110-4*i;y2=70
                if kind=='overlap':x1,x2,y2=30+5*i,100-5*i,20
                boxes=[[x1,20,x1+20,40],[x2,y2,x2+20,y2+20]]
                image=Image.new('RGB',(160,120),'white');draw=ImageDraw.Draw(image)
                for j,box in enumerate(boxes):
                    if kind=='short_gap' and i==3 and j==0:continue
                    draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill='black')
                image.save(folder/f'{i:03d}.png')
                truth.append({'timestamp':i/4,'source_size':[300,225],
                              'objects':[{'gt_id':str(j),'class':'quadrilateral','box':[v*1.875 for v in box]} for j,box in enumerate(boxes)]})
            clip=folder/'clip.mp4'
            run_decoder(['ffmpeg','-v','error','-nostdin','-threads','1','-framerate','4','-i',str(folder/'%03d.png'),
                         '-c:v','mpeg4','-q:v','2','-pix_fmt','yuv420p',str(clip)],20)
            before=hash_file(clip)[0]
            report=observe_video(clip,root,fps=4,max_seconds=2,tracking_mode='conservative')
            metrics=evaluate(truth,report['frames'])
            cases.append({'scenario':kind,'metrics':metrics,'source_preserved':before==hash_file(clip)[0]==report['source_sha256'],
                          'sample_timestamps':[f['timestamp'] for f in report['frames']],
                          'unresolved_observations':sum(len(f['unresolved_detection_indices']) for f in report['frames']),
                          'resources':report['resources'],'performance':report['performance'],
                          'temporal_performance':report['temporal_performance']})
    totals={k:sum(c['metrics'][k] for c in cases) for k in ('tp','fp','fn','identity_switches','fragmentations','truth_observations')}
    return {'generated_clips':3,'decoded_frames':sum(c['metrics']['frames'] for c in cases),'totals':totals,'cases':cases,
            'representative_validation':False,'scope':'generated renderer boxes, actual MPEG4 encode/decode and geometric segmentation; not real application captures'}
