from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def list_media(self, prefix: str) -> List[Dict[str, Any]]:
        base = (self._root / prefix).resolve()
        if not str(base).startswith(str(self._root.resolve())):
            return []
        if not base.exists():
            return []
        items: List[Dict[str, Any]] = []
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            rel = path.relative_to(self._root).as_posix()
            stat = path.stat()
            items.append(
                {
                    "path": rel,
                    "url": self.build_url(rel),
                    "size": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                }
            )
        return items
