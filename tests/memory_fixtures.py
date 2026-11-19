from packet_fixtures import packet
from seye.core.storage import checksum

def record(value,label=None):
    return {'schema_version':1,'features':None,'packet':packet(value),
            'provenance':{'kind':'numeric_memory_fixture','source_sha256':checksum({'numeric_fixture':value})},
            'fixture_label':label}
