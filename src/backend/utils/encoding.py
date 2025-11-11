from __future__ import annotations

from typing import Tuple

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


def encode_jpeg(frame: np.ndarray, quality: int = 80) -> bytes:
    """Encode an RGB frame into JPEG bytes."""
    if cv2 is None:
        raise RuntimeError("OpenCV is required to encode frames to JPEG.")
    encode_params: Tuple[int, int] = (cv2.IMWRITE_JPEG_QUALITY, quality)
    success, buffer = cv2.imencode(".jpg", frame[:, :, ::-1], encode_params)
    if not success:
        raise RuntimeError("Encoding frame to JPEG failed.")
    return buffer.tobytes()

