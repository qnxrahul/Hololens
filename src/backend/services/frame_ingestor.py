from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover - OpenCV is optional at scaffold time
    cv2 = None


@dataclass
class FrameIngestSettings:
    """Configuration for frame ingestion."""

    source_uri: str
    target_fps: Optional[float] = None
    warmup_frames: int = 5


class FrameIngestor:
    """Pulls frames from a video source and yields them asynchronously."""

    def __init__(self, settings: FrameIngestSettings) -> None:
        self._settings = settings
        self._capture: Optional["cv2.VideoCapture"] = None
        self._lock = asyncio.Lock()

    async def _ensure_capture(self) -> "cv2.VideoCapture":
        if cv2 is None:
            raise RuntimeError(
                "OpenCV is required for FrameIngestor; install opencv-python-headless."
            )

        async with self._lock:
            if self._capture is None:
                self._capture = await asyncio.to_thread(cv2.VideoCapture, self._settings.source_uri)
                if not self._capture or not self._capture.isOpened():
                    raise RuntimeError(f"Unable to open video source: {self._settings.source_uri}")
                # Warmup frames for camera auto exposure, etc.
                for _ in range(self._settings.warmup_frames):
                    await asyncio.to_thread(self._capture.read)
        return self._capture

    async def frames(self) -> AsyncGenerator[np.ndarray, None]:
        """Asynchronously generate frames from the source."""
        capture = await self._ensure_capture()
        while True:
            ret, frame = await asyncio.to_thread(capture.read)
            if not ret:
                break
            yield frame
            if self._settings.target_fps:
                await asyncio.sleep(1.0 / self._settings.target_fps)

    async def close(self) -> None:
        async with self._lock:
            if self._capture is not None:
                await asyncio.to_thread(self._capture.release)
                self._capture = None

