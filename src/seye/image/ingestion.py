"""Bounded local image ingestion, with explicit allowed source roots."""
import hashlib
import io
from PIL import Image, ImageOps
from seye.core.files import read_bounded, resolve_path

MAX_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 20_000_000


def load_image(path, allowed_root=None, max_bytes=MAX_BYTES, max_pixels=MAX_PIXELS):
    path = resolve_path(path)
    if allowed_root is not None and not path.is_relative_to(resolve_path(allowed_root)):
        raise ValueError('Image is outside the permitted source root')
    if type(max_bytes) is not int or not 1<=max_bytes<=MAX_BYTES or type(max_pixels) is not int or not 1<=max_pixels<=MAX_PIXELS:
        raise ValueError('Resource limits must be positive integers within the global byte/pixel caps')
    if not path.is_file() or path.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        raise ValueError('Expected a local JPEG or PNG file')
    raw = read_bounded(path, max_bytes)
    try:
        with Image.open(io.BytesIO(raw)) as original:
            if original.format not in ('PNG', 'JPEG'):
                raise ValueError('Image content must be PNG or JPEG')
            expected_format = 'PNG' if path.suffix.lower() == '.png' else 'JPEG'
            if original.format != expected_format:
                raise ValueError('Image format does not match its filename extension')
            if original.width * original.height > max_pixels:
                raise ValueError('Image exceeds pixel limit')
            if getattr(original, 'n_frames', 1) != 1:
                raise ValueError('Animated inputs require a video ingestion interface')
            if original.format == 'PNG':
                original.verify()
        with Image.open(io.BytesIO(raw)) as original:
            # No-orientation inputs do not need the extra full-image copy made
            # by exif_transpose. RGB conversion still detaches from the stream.
            orientation=original.getexif().get(274,1)
            if orientation in (2,3,4,5,6,7,8):
                rgb=ImageOps.exif_transpose(original).convert('RGB')
            else:
                rgb=original.convert('RGB')
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError(f'Image decoding failed: {error}') from error
    return rgb, {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                 'size': list(rgb.size), 'coordinates': 'EXIF-oriented source pixels'}
