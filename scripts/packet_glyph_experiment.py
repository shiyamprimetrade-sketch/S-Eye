"""Independently rendered generated captures; synthetic labels are renderer metadata."""
import hashlib
from PIL import Image,ImageDraw
from seye.recognition.pipeline import FeaturePipeline
from seye.learning.packet_prototypes import fit,UNKNOWN
from seye.learning.packet_calibration import bind
from seye.learning.packet_evaluation import evaluate
from seye.core.storage import checksum


def render(shape,x,y,shade=24):
    image=Image.new('RGB',(128,96),(shade,shade,shade));draw=ImageDraw.Draw(image);color='white'
    if shape=='run':draw.polygon([(x+3,y+2),(x+22,y+8),(x+3,y+14)],fill=color)
    elif shape=='stop':draw.rectangle((x+4,y+2,x+19,y+13),fill=color)
    elif shape=='menu':
        for dy in (2,7,12):draw.rectangle((x+2,y+dy,x+21,y+dy+1),fill=color)
    elif shape=='plus':
        draw.rectangle((x+10,y,x+13,y+15),fill=color);draw.rectangle((x,y+6,x+23,y+9),fill=color)
    elif shape=='chevron':draw.line([(x+3,y),(x+20,y+8),(x+3,y+15)],fill=color,width=3)
    else:raise ValueError('Unknown renderer glyph')
    return image


def dataset():
    pipeline=FeaturePipeline();splits={key:[] for key in ('train','validation','test')}
    locations={'train':[(12,16),(16,16),(20,16)],'validation':[(24,16),(28,20)],'test':[(32,16),(36,24)]}
    for split,points in locations.items():
        for shape in ('run','stop','menu'):
            for i,(x,y) in enumerate(points):
                image=render(shape,x,y,24+i);identifier=f'{split}-{shape}-{i}'
                splits[split].append({'id':identifier,'group':identifier,'label':shape,'source_kind':'generated',
                    'content_sha256':hashlib.sha256(f'RGB:{image.width}:{image.height}:'.encode()+image.tobytes()).hexdigest(),
                    'packet':pipeline.extract(image,['geometry','appearance'])})
    for shape in ('plus','chevron'):
        for i,(x,y) in enumerate(locations['test']):
            image=render(shape,x,y,28+i);identifier=f'test-unknown-{shape}-{i}'
            splits['test'].append({'id':identifier,'group':identifier,'label':UNKNOWN,'source_kind':'generated','renderer_shape':shape,
                'content_sha256':hashlib.sha256(f'RGB:{image.width}:{image.height}:'.encode()+image.tobytes()).hexdigest(),
                'packet':pipeline.extract(image,['geometry','appearance'])})
    return splits


def run():
    splits=dataset();model=fit(splits['train'],splits['validation']);calibration=bind(model,splits['validation'])
    report=evaluate(model,splits['test'],calibration)
    protocol={'classes':['run','stop','menu'],'unknown_designs':['plus','chevron'],'components':['geometry','appearance'],
              'min_margin':.005,'radius_floor':.015,'validation_radius_factor':1.1,'training':9,'validation':6,'testing':10,
              'selection':'fixed renderer coordinates and settings; no test fitting or parameter search'}
    return {'protocol':protocol,'protocol_sha256':checksum(protocol),'dataset_sha256':checksum(splits),'report':report,
            'limitations':['Generated glyphs share renderer; no representative application validation.',
                           'Numeric support calibration does not improve recognition labels.',
                           'Position/theme changes and unknown inputs can expose failures; no minimum accuracy target is assumed.']}
