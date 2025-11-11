from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MediaItem(BaseModel):
    path: str
    url: str
    size: int
    modified_at: datetime

