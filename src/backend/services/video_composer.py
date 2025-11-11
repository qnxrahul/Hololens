from __future__ import annotations

from typing import Tuple

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


class VideoComposer:
    """Utility for building picture-in-picture layouts."""

    def __init__(self, border_color: Tuple[int, int, int] = (0, 255, 0), border_thickness: int = 2) -> None:
        self.border_color = border_color
        self.border_thickness = border_thickness

    def compose(self, base_frame: np.ndarray, inset_frame: np.ndarray, *, position: Tuple[int, int], size: Tuple[int, int]) -> np.ndarray:
        """Embed inset_frame into base_frame at the requested coordinates."""
        if base_frame.ndim != 3 or inset_frame.ndim != 3:
            raise ValueError("Expected color frames with shape [H, W, C].")
        h, w, _ = base_frame.shape
        inset_w, inset_h = size
        x, y = position

        if x < 0 or y < 0 or x + inset_w > w or y + inset_h > h:
            raise ValueError("Inset frame does not fit within the base frame at the requested position.")

        resized_inset = self._resize_frame(inset_frame, (inset_w, inset_h))
        composed = base_frame.copy()
        composed[y : y + inset_h, x : x + inset_w] = resized_inset

        # Draw border
        if self.border_thickness > 0:
            self._draw_border(composed, x, y, inset_w, inset_h)

        return composed

    def _resize_frame(self, frame: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        width, height = size
        if cv2 is None:
            # Fallback to naive numpy slicing if OpenCV is unavailable.
            y_indices = np.linspace(0, frame.shape[0] - 1, height).astype(int)
            x_indices = np.linspace(0, frame.shape[1] - 1, width).astype(int)
            return frame[np.ix_(y_indices, x_indices)]
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    def _draw_border(self, frame: np.ndarray, x: int, y: int, width: int, height: int) -> None:
        if cv2 is None:
            # Simple numpy border
            frame[y : y + height, x : x + self.border_thickness] = self.border_color
            frame[y : y + height, x + width - self.border_thickness : x + width] = self.border_color
            frame[y : y + self.border_thickness, x : x + width] = self.border_color
            frame[y + height - self.border_thickness : y + height, x : x + width] = self.border_color
        else:
            cv2.rectangle(
                frame,
                (x, y),
                (x + width, y + height),
                color=self.border_color,
                thickness=self.border_thickness,
            )

