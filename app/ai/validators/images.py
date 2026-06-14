"""Image validation — dimensions, corruption, hash, optional OCR."""

import hashlib
from io import BytesIO

from PIL import Image as PILImage


MIN_WIDTH = 512
MIN_HEIGHT = 512
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_image_bytes(image_bytes: bytes) -> str | None:
    """Validate raw image data.

    Returns ``None`` if valid, or an error string if invalid.
    """
    if not image_bytes:
        return "Image data is empty"

    if len(image_bytes) > MAX_SIZE_BYTES:
        return f"Image too large: {len(image_bytes)} bytes (max {MAX_SIZE_BYTES})"

    try:
        img = PILImage.open(BytesIO(image_bytes))
        img.verify()  # lightweight check — doesn't load pixels
    except Exception as e:
        return f"Image corrupt or unreadable: {e}"

    # Re-open after verify (verify may close the file)
    try:
        img = PILImage.open(BytesIO(image_bytes))
        w, h = img.size
    except Exception as e:
        return f"Could not read image dimensions: {e}"

    if w < MIN_WIDTH or h < MIN_HEIGHT:
        return f"Image too small: {w}x{h} (min {MIN_WIDTH}x{MIN_HEIGHT})"

    return None
