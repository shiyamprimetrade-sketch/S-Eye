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
        with self.assertRaises(ValueError):prediction_summary({'selection':{'accepted':True,'label':'x'*129}})
        output=document('<script>bad()</script>','<p>safe internal body</p>')
        self.assertNotIn('<script>bad()',output);self.assertIn('&lt;script&gt;',output)

    def test_actual_supplied_model_decision_is_reported_and_label_is_escaped(self):
        from seye.recognition.pipeline import FeaturePipeline
        from seye.learning.packet_prototypes import fit,save
        from seye.core.storage import checksum
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png';image=Image.new('RGB',(80,60),'white');ImageDraw.Draw(image).rectangle((10,10,40,40),fill='black');image.save(source)
            blank=Image.new('RGB',(80,60),'white');pipeline=FeaturePipeline()
            packets=[pipeline.extract(im,['appearance']) for im in (image,blank)];labels=['<script>bad()</script>','blank']
            def row(prefix,index):
                identifier=prefix+str(index)
                return {'id':identifier,'group':identifier,'label':labels[index],'packet':packets[index],
                        'content_sha256':checksum({'generated_descriptor_fixture':identifier,'packet':packets[index]})}
            model=fit([row('train',i) for i in range(2)],[row('validation',i) for i in range(2)])
            save(root/'model.json',model);ingest([source],root/'workspace',root)
            build_report(root/'workspace',root/'report',root,root/'model.json')
            report=read_json(root/'report'/'report.json');decision=report['items'][0]['decision']
            self.assertEqual(decision['status'],'model_label');self.assertEqual(decision['label'],labels[0])
            text=(root/'report'/'report.html').read_text();self.assertNotIn('<script>bad()',text);self.assertIn('&lt;script&gt;',text)
