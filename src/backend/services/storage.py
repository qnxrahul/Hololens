from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LocalStorageSettings:
    root: Path
    base_url: str = "/media"


class LocalStorageClient:
    """Simple filesystem-backed media storage for development and on-prem deployments."""

    def __init__(self, settings: LocalStorageSettings) -> None:
        self._root = settings.root
        self._base_url = settings.base_url.rstrip("/")
        self._root.mkdir(parents=True, exist_ok=True)
        logger.info("Local storage using %s", self._root)

    def ensure_ready(self) -> None:
        """Already handled in __init__; provided for interface parity."""
        self._root.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, relative_path: str, data: bytes) -> Path:
        target = (self._root / relative_path).resolve()
        if not str(target).startswith(str(self._root.resolve())):
            raise ValueError("Attempt to write outside of storage root")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        logger.debug("Saved media blob to %s", target)
        return target

    def build_url(self, relative_path: str) -> str:
        safe_path = "/".join(part for part in Path(relative_path).parts if part not in {"..", ""})
        return f"{self._base_url}/{safe_path}"

    def resolve_path(self, relative_path: str) -> Optional[Path]:
        target = (self._root / relative_path).resolve()
        if not target.exists():
            return None
        if not str(target).startswith(str(self._root.resolve())):
            return None
        return target
