"""Bounded opt-in descriptor LRU; image bytes are validated on every lookup."""
from collections import OrderedDict
import sys
from seye.image.ingestion import load_image
from seye.recognition.features import FEATURE_VERSION, extract


class FeatureCache:
    def __init__(self, max_entries=64, max_bytes=2 * 1024 * 1024):
        if type(max_entries) is not int or not 1 <= max_entries <= 10000 or type(max_bytes) is not int or not 1 <= max_bytes <= 64 * 1024 * 1024:
            raise ValueError('Invalid bounded cache configuration')
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self.rows = OrderedDict(); self.bytes = 0
        self.hits = self.misses = self.evictions = 0

    def from_file(self, path, allowed_root=None):
        image, source = load_image(path, allowed_root=allowed_root)
        key = (FEATURE_VERSION, source['sha256'])
        if key in self.rows:
            self.hits += 1; self.rows.move_to_end(key)
            return list(self.rows[key][0]), source
        self.misses += 1; values = extract(image)
        size = sys.getsizeof(values) + sum(sys.getsizeof(v) for v in values) + sys.getsizeof(key) + sum(sys.getsizeof(v) for v in key)
        if size <= self.max_bytes:
            while self.rows and (len(self.rows) >= self.max_entries or self.bytes + size > self.max_bytes):
                _, (_, removed) = self.rows.popitem(last=False); self.bytes -= removed; self.evictions += 1
            self.rows[key] = (list(values), size); self.bytes += size
        return values, source

    def statistics(self):
        return {'entries': len(self.rows), 'estimated_python_bytes': self.bytes, 'hits': self.hits,
                'misses': self.misses, 'evictions': self.evictions,
                'scope': 'descriptor cache only; source read/hash/decode still occurs; byte estimate is not process RSS'}
