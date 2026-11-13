"""New protocol fixed before fitting; correlated generated captures only."""
import hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from packet_glyph_experiment import render
from seye.core.storage import read_json
from seye.recognition.pipeline import FeaturePipeline
from seye.learning.packet_prototypes import UNKNOWN


def protocol():return read_json(Path(__file__).resolve().parents[1]/'experiments/stages111_120_protocol.json')


def dataset(components=('shape',)):
    p=protocol();pipeline=FeaturePipeline();splits={name:[] for name in ('train','validation','test')}
    for name in splits:
        shapes=p['known_classes']+(p['unknown_designs'] if name=='test' else [])
        for shape in shapes:
            for i,(x,y) in enumerate(p[name+'_positions']):
                shade=20+i
                if shape in p['known_classes']:image=render(shape,x,y,shade)
                else:
                    image=Image.new('RGB',(128,96),(shade,)*3);draw=ImageDraw.Draw(image)
                    if shape=='ring':draw.ellipse((x+2,y,x+21,y+15),outline='white',width=2)
                    elif shape=='diamond':draw.polygon([(x+12,y),(x+23,y+8),(x+12,y+15),(x,y+8)],fill='white')
                    else:raise ValueError('Unknown generated design')
                identifier=f'{name}-{shape}-{i}'
                splits[name].append({'id':identifier,'group':identifier,'label':shape if shape in p['known_classes'] else UNKNOWN,
                                    'source_kind':'generated','annotation_origin':'renderer','source_size':[128,96],'box':[x,y,x+24,y+16],
                                    'content_sha256':hashlib.sha256(f'RGB:{image.width}:{image.height}:'.encode()+image.tobytes()).hexdigest(),
                                    'packet':pipeline.extract(image,list(components))})
    return splits
