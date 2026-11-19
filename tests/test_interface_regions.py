import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image,ImageDraw
from seye.interface.regions import edge_mask,propose_regions
from seye.integration.service import Permissions,handle
from seye.memory.store import Memory
from seye.detection.metrics import box_iou

spec=importlib.util.spec_from_file_location('stage91',Path(__file__).parents[1]/'scripts/benchmark_stage91.py')
benchmark=importlib.util.module_from_spec(spec);spec.loader.exec_module(benchmark)


def scene():
    image=Image.new('RGB',(160,96),'black')
    ImageDraw.Draw(image).rectangle((24,16,63,39),fill='white')
    return image


class InterfaceRegionTests(unittest.TestCase):
    def test_template_free_localization_and_evidence_are_deterministic(self):
        image=scene();before=image.tobytes();first=propose_regions(image)
        self.assertEqual(first,propose_regions(image));self.assertEqual(image.tobytes(),before)
        self.assertEqual(len(first['regions']),1)
        region=first['regions'][0];self.assertGreater(box_iou(region['box'],[24,16,64,40]),.9)
        self.assertIsNone(region['semantic_label']);self.assertEqual(region['clickability'],'unknown')
        self.assertTrue(first['complete'])

    def test_blank_noise_low_contrast_and_chromatic_edges(self):
        for image in (Image.new('RGB',(160,96),'gray'),):
            self.assertEqual(propose_regions(image)['regions'],[])
        for metadata,image in benchmark.fixtures():
            if metadata['state'] in ('blank','noise','low_contrast'):
                self.assertEqual(propose_regions(image)['regions'],[],metadata['id'])
            if metadata['id']=='chromatic-edge':
                self.assertEqual(len(propose_regions(image)['regions']),1)

    def test_budget_configuration_and_fragment_limits(self):
        for options in ({'edge_threshold':True},{'edge_threshold':0},{'min_width':1},{'max_regions':129}):
            with self.assertRaises(ValueError):propose_regions(scene(),**options)
        with patch('seye.interface.regions.MAX_PIXELS',10):
            with self.assertRaisesRegex(ValueError,'pixel budget'):edge_mask(scene())
        with patch('seye.interface.regions.MAX_EDGE_PIXELS',10):
            with self.assertRaisesRegex(ValueError,'edge-pixel budget'):propose_regions(scene())
        image=scene();ImageDraw.Draw(image).rectangle((90,16,129,39),fill='white')
        with patch('seye.interface.regions.MAX_COMPONENTS',1):
            with self.assertRaisesRegex(ValueError,'component budget'):propose_regions(image)

    def test_region_limit_is_explicit_partial_output(self):
        image=scene();ImageDraw.Draw(image).rectangle((90,16,129,39),fill='white')
        result=propose_regions(image,max_regions=1)
        self.assertEqual(result['candidate_count'],2);self.assertEqual(len(result['regions']),1)
        self.assertTrue(result['truncated']);self.assertFalse(result['complete'])

    def test_scoped_json_and_memory_work_without_a_template(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);scene().save(root/'screen.png')
            request={'schema_version':1,'request_id':'regions','action':'observe_interface',
                     'image':str(root/'screen.png'),'region_proposals':True,'memory':str(root/'memory.sqlite3')}
            grants=Permissions((str(root),),(str(root),),memory=True)
            response=handle(request,grants);self.assertTrue(response['success'],response)
            result=response['result'];self.assertEqual(result['elements'],[])
            self.assertEqual(len(result['region_proposals']['regions']),1)
            self.assertIn({'type':'region_hypotheses','count':1,'complete':True},result['signals'])
            memory=Memory(root/'memory.sqlite3',read_only=True)
            try:self.assertEqual(memory.get(result['observation_id'])['analysis']['region_proposals'],result['region_proposals'])
            finally:memory.close()
            self.assertFalse(handle(request,Permissions())['success'])
            self.assertFalse(handle(dict(request,region_proposals='true'),grants)['success'])
            self.assertFalse(handle(dict(request,action='click'),grants)['success'])

    def test_generated_experiment_retains_overlap_misses_and_outline_duplicates(self):
        report=benchmark.run();self.assertEqual(report,benchmark.run())
        self.assertEqual(report['completed_cases'],33)
        self.assertEqual(report['localization'],{'tp':25,'fp':8,'fn':12})
        self.assertEqual(report['by_condition']['state']['overlap']['fn'],8)
        self.assertEqual(report['by_condition']['state']['outlined']['fp'],4)
        self.assertIsNone(report['representative_application_accuracy'])
