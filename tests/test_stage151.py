import unittest,tempfile,io
from pathlib import Path
from PIL import Image,ImageOps
from seye.image.ingestion import load_image,MAX_BYTES,MAX_PIXELS

class DecodeTests(unittest.TestCase):
    def test_orientation_palette_gray_rgb_and_detachment_preserve_pixels(self):
        with tempfile.TemporaryDirectory() as d:
            for format_name,modes in (('PNG',('RGB','L','P','RGBA')),('JPEG',('RGB','L'))):
                path=Path(d)/('image.png' if format_name=='PNG' else 'image.jpg')
                for mode in modes:
                    for orientation in range(1,9):
                        im=Image.new('RGB',(9,6),'red');im.putpixel((2,3),(0,0,0));im=im.convert(mode)
                        exif=Image.Exif();exif[274]=orientation;im.save(path,format=format_name,exif=exif)
                        raw=path.read_bytes()
                        with Image.open(io.BytesIO(raw)) as source:expected=ImageOps.exif_transpose(source).convert('RGB')
                        actual,metadata=load_image(path,d)
                        self.assertEqual(actual.size,expected.size);self.assertEqual(actual.tobytes(),expected.tobytes())
                        path.unlink();self.assertEqual(actual.getpixel((0,0)),expected.getpixel((0,0)))

    def test_decode_bounds_apply_before_pixel_decode(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';Image.new('RGB',(100,80)).save(path)
            for limits in ({'max_pixels':10},{'max_bytes':1},{'max_pixels':MAX_PIXELS+1},{'max_bytes':MAX_BYTES+1},{'max_bytes':True}):
                with self.assertRaises(ValueError):load_image(path,**limits)
            with self.assertRaises(ValueError):load_image(path,Path(d)/'elsewhere')
            path.write_bytes(b'broken png')
            with self.assertRaises(ValueError):load_image(path)
