import copy,unittest
from packet_fixtures import packet,data
from seye.core.storage import checksum
from seye.recognition.similarity import validate_packet
from seye.learning.packet_prototypes import validate_records,fit
from seye.learning.packet_calibration import bind,support
from seye.learning.versioning import validate_snapshot
class PacketContractValidationTests(unittest.TestCase):
    def test_bad_component_and_record_types_fail_explicitly(self):
        p=packet(0);p['schema']['components']=[None];p['schema_sha256']=checksum(p['schema'])
        with self.assertRaises(ValueError):validate_packet(p)
        with self.assertRaises(ValueError):validate_records([None])
    def test_rehashed_malformed_calibrator_fails_without_worker_timeout(self):
        train,val=data();model=fit(train,val);binding=bind(model,val);binding['calibrator']=None
        binding['calibration_sha256']=checksum({k:v for k,v in binding.items() if k!='calibration_sha256'})
        with self.assertRaises(ValueError):support(model,binding,packet(0))
    def test_rehashed_revision_still_needs_version_identity(self):
        payload={'schema':'seye-dataset-revision-v1','images':[{}]}
        with self.assertRaises(ValueError):validate_snapshot({'payload':payload,'sha256':checksum(payload)})
