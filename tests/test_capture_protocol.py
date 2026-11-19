import unittest
import analyze_image
from seye.core.capture_protocol import assess

class CaptureProtocolTests(unittest.TestCase):
    def rows(self):
        return [dict(id=str(i),sha256=f'{i:064x}',source_kind='photograph',human_confirmed=True,
                     expected_classes=['circle'],target_group='same-shapes',lighting=['diffuse','dim','diffuse'][i],
                     camera_angle=['frontal','frontal','oblique'][i]) for i in range(3)]

    def test_declared_coverage_is_not_recognition_validation(self):
        report=assess(self.rows());self.assertTrue(report['ready']);self.assertFalse(report['recognition_accuracy_validated'])

    def test_repeated_bytes_cannot_satisfy_capture_count(self):
        rows=self.rows();rows[1]['sha256']=rows[0]['sha256'];self.assertFalse(assess(rows)['ready'])

    def test_screenshots_simulated_conditions_and_unreviewed_labels_fail(self):
        for field,value in [('source_kind','screenshot'),('human_confirmed',False),('target_group',None)]:
            rows=self.rows();rows[0][field]=value;self.assertFalse(assess(rows)['ready'])
        rows=self.rows()
        for row in rows:row['lighting']='unknown';row['camera_angle']='unmeasured'
        self.assertFalse(assess(rows)['ready'])

    def test_empty_and_changed_target_inventory_fail(self):
        self.assertFalse(assess([])['ready'])
        rows=self.rows();rows[1]['expected_classes']=['triangle'];self.assertFalse(assess(rows)['ready'])
