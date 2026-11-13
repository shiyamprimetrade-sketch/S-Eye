import copy
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
spec=importlib.util.spec_from_file_location('stage90',Path(__file__).parents[1]/'scripts/benchmark_stage90.py')
benchmark=importlib.util.module_from_spec(spec);spec.loader.exec_module(benchmark)


class BenchmarkPortabilityTests(unittest.TestCase):
    def test_encoded_bytes_can_vary_but_pixels_and_results_cannot(self):
        frozen={'summary':{'tp':1},'cases':[{'id':'one','observed_status':'visual_candidate','source_sha256':'encoded-linux'}]}
        pixels={'one':{'source_pixel_sha256':'rgb-a','previous_pixel_sha256':'rgb-b','template_pixel_sha256':'rgb-c'}}
        actual=copy.deepcopy(frozen);actual['cases'][0].update(pixels['one'],source_sha256='encoded-windows')
        self.assertTrue(benchmark.frozen_equivalent(actual,frozen,pixels))
        modified=copy.deepcopy(actual);modified['cases'][0]['source_pixel_sha256']='different-pixels'
        self.assertFalse(benchmark.frozen_equivalent(modified,frozen,pixels))
        modified=copy.deepcopy(actual);modified['cases'][0]['observed_status']='not_found'
        self.assertFalse(benchmark.frozen_equivalent(modified,frozen,pixels))
        modified=copy.deepcopy(actual);modified['summary']['tp']=0
        self.assertFalse(benchmark.frozen_equivalent(modified,frozen,pixels))
