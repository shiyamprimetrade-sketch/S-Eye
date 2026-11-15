import unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from seye.integration.questions import ask

class GroundedQuestionTests(unittest.TestCase):
    def test_counts_boxes_and_unchanged_pixels_have_bound_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';image=Image.new('RGB',(80,60),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
            count=ask(path,'count_proposed_regions');boxes=ask(path,'list_region_boxes')
            self.assertEqual(count['answer'],len(boxes['answer']))
            self.assertEqual(len(count['evidence'][0]['source']['sha256']),64)
            unchanged=ask(path,'changed_pixel_fraction',previous=path)
            self.assertEqual(unchanged['answer'],0);self.assertEqual(unchanged['status'],'answered')
            self.assertFalse(count['automatic_action_authorized'])

    def test_text_and_executable_looking_questions_abstain_without_file_read(self):
        for question in ('read_text','which button should I click?',"__import__('os').system('anything')"):
            answer=ask('/missing.png',question)
            self.assertEqual(answer['status'],'unsupported');self.assertIsNone(answer['answer']);self.assertEqual(answer['evidence'],[])
        with self.assertRaises(ValueError):ask('/missing.png',['not a string'])
