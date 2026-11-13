import unittest,tempfile
from pathlib import Path
from PIL import Image
from seye.recognition.packet_cache import PacketCache

class PacketCacheTests(unittest.TestCase):
    def test_schema_revision_copy_and_root_checks(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'a.png';Image.new('RGB',(40,30),'white').save(path);cache=PacketCache()
            a,_=cache.from_file(path,['appearance'],d);b,_=cache.from_file(path,['appearance'],d)
            self.assertEqual(a,b);b['features'][0]=100
            self.assertNotEqual(cache.from_file(path,['appearance'],d)[0]['features'][0],100)
            cache.from_file(path,['shape'],d);self.assertEqual(cache.misses,2)
            Image.new('RGB',(40,30),'black').save(path);cache.from_file(path,['appearance'],d)
            self.assertEqual(cache.misses,3)
            with self.assertRaises(ValueError):cache.from_file(path,['appearance'],Path(d)/'elsewhere')
            cache.clear();self.assertEqual(cache.statistics()['entries'],0);self.assertEqual(cache.hits,0)

    def test_lru_and_oversized_packet_never_break_budgets(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for i,color in enumerate(('white','black','red')):
                p=Path(d)/f'{i}.png';Image.new('RGB',(30,30),color).save(p);paths.append(p)
            cache=PacketCache(max_entries=2)
            for p in (paths[0],paths[1],paths[0],paths[2],paths[1]):cache.from_file(p,['appearance'])
            self.assertEqual(cache.hits,1);self.assertEqual(cache.evictions,2);self.assertEqual(cache.statistics()['entries'],2)
            tiny=PacketCache(max_bytes=1);tiny.from_file(paths[0]);self.assertEqual(tiny.statistics()['entries'],0)
