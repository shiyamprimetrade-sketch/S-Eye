import unittest
from PIL import Image, ImageDraw
from generalization import transform, EXTRA_VARIANTS

class Stage88Tests(unittest.TestCase):
    def test_stress_variants_are_deterministic_and_preserve_original(self):
        image=Image.new('RGB',(120,100),'white');ImageDraw.Draw(image).rectangle((20,20,80,80),outline='black',width=4)
        before=image.tobytes()
        for variant in EXTRA_VARIANTS:
            first=transform(image,variant)
            self.assertEqual(first.size,image.size)
            self.assertEqual(first.tobytes(),transform(image,variant).tobytes())
            self.assertNotEqual(first.tobytes(),before)
        self.assertEqual(image.tobytes(),before)
