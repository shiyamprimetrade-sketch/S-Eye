"""Labeled generated retrieval test; labels score results but never rank them."""
import hashlib,io,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from packet_glyph_experiment import render
from seye.memory.store import Memory
from seye.memory.identity import pixel_identity
from seye.memory.packet_index import rebuild,query
from seye.recognition.pipeline import FeaturePipeline


def run():
    pipeline=FeaturePipeline();results=[];top1=recall3=unknown_rejected=ambiguous=0
    with tempfile.TemporaryDirectory() as directory:
        memory=Memory(Path(directory)/'memory.sqlite3')
        try:
            for label in ('run','stop','menu'):
                for i,x in enumerate((8,14)):
                    image=render(label,x,12+i*4,24+i);encoded=io.BytesIO();image.save(encoded,format='PNG')
                    memory.put({'schema_version':1,'features':None,'packet':pipeline.extract(image,['shape']),
                                'fixture_label':label,'provenance':{'kind':'generated_retrieval_fixture','source_sha256':hashlib.sha256(encoded.getvalue()).hexdigest(),'pixel_sha256':pixel_identity(image)}})
            rebuild(memory)
            for label in ('run','stop','menu','ring','diamond'):
                for i,x in enumerate((76,84)):
                    if label in ('run','stop','menu'):image=render(label,x,18+i*18,28+i)
                    else:
                        image=Image.new('RGB',(128,96),(28+i,)*3);draw=ImageDraw.Draw(image);y=18+i*18
                        if label=='ring':draw.ellipse((x+2,y,x+21,y+15),outline='white',width=2)
                        else:draw.polygon([(x+12,y),(x+23,y+8),(x+12,y+15),(x,y+8)],fill='white')
                    packet=pipeline.extract(image,['shape']);r=query(memory,packet,limit=3,maximum_distance=.015)
                    labels=[memory.get(item['id'])['fixture_label'] for item in r['matches']]
                    known=label in ('run','stop','menu')
                    if known:top1+=bool(labels) and labels[0]==label;recall3+=label in labels;ambiguous+=r['ambiguous_top_distance']
                    else:unknown_rejected+=not labels
                    results.append({'id':f'{label}-{i}','expected_category':label if known else '__unknown__','returned_oracle_labels':labels,
                                    'distances':[m['distance'] for m in r['matches']],'ambiguous_top_distance':r['ambiguous_top_distance']})
        finally:memory.close()
    return {'gallery':6,'known_queries':6,'unknown_queries':4,'top1_category_correct':top1,'category_recall_at3':recall3,
            'unknown_queries_without_match':unknown_rejected,'ambiguous_known_queries':ambiguous,'maximum_distance':.015,
            'results':results,'representative_retrieval_quality_validated':False,
            'limitations':['Shared renderer and centered glyphs, not independent applications.','Same-category top-distance ties do not establish a unique persistent object.','Distance cutoff inherited before querying; no test fitting.']}
