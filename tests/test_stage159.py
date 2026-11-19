import unittest
from seye.performance.platforms import host_report,coverage

class HostMeasurementTests(unittest.TestCase):
    def test_running_host_metadata_is_bounded_and_has_no_device_success_claim(self):
        host=host_report();self.assertIn(host['pointer_bits'],(32,64))
        self.assertIsInstance(host['python_version'],str)
        self.assertFalse(host['device_performance_validated'])
        self.assertNotIn('hostname',host);self.assertNotIn('username',host)
        self.assertFalse(coverage([host])['android_hardware_validation'])

    def test_caller_reports_and_android_clues_cannot_certify_hardware(self):
        linux=dict(host_report(),system='Linux',android_candidate=False)
        windows=dict(linux,system='Windows');candidate=dict(linux,system='Android',android_candidate=True)
        r=coverage([linux,windows,candidate]);self.assertTrue(r['linux_reported'] and r['windows_reported'])
        self.assertTrue(r['android_candidate_reported']);self.assertFalse(r['android_hardware_validation'])
        with self.assertRaises(ValueError):coverage([dict(linux,schema_version=True)])
