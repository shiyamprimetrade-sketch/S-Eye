import unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from seye.local.workspace import ingest
from seye.local.reports import build_report,prediction_summary,document
from seye.core.storage import read_json

class EvidenceReportTests(unittest.TestCase):
    def test_offline_report_preserves_count_source_and_no_model_status(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'source.png';image=Image.new('RGB',(80,60),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
            ingest([path],root/'workspace',root);build_report(root/'workspace',root/'report',root)
            report=read_json(root/'report'/'report.json');row=report['items'][0]
            self.assertEqual(row['region_count'],len(row['boxes']));self.assertEqual(row['decision']['status'],'not_requested')
            self.assertFalse(report['semantic_recognition_validated']);self.assertTrue((root/'report'/'report.html').is_file())

    def test_labels_never_become_probabilities_or_executable_title_markup(self):
        decision=prediction_summary({'selection':{'accepted':True,'label':'<script>bad()</script>','reason':'fixture','nearest_distance':0,'rejection_radius':.1}})
        self.assertIsNone(decision['confidence_probability'])
        output=document('<script>bad()</script>','<p>safe internal body</p>')
        self.assertNotIn('<script>bad()',output);self.assertIn('&lt;script&gt;',output)
