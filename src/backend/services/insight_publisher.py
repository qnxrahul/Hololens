from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Set

from fastapi import WebSocket


class InsightPublisher:
    """Broadcasts augmented frames and metadata to connected subscribers."""

    def __init__(self) -> None:
        self._subscribers: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def add_subscriber(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._subscribers.add(websocket)

    async def remove_subscriber(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self._subscribers:
                self._subscribers.remove(websocket)
        await websocket.close()

    async def broadcast_metadata(self, payload: Dict[str, Any]) -> None:
        message = json.dumps({"type": "metadata", "payload": payload})
        await self._broadcast_text(message)

    async def broadcast_frame(self, frame_bytes: bytes) -> None:
        await self._broadcast_binary(frame_bytes)

    async def _broadcast_text(self, data: str) -> None:
        async with self._lock:
            subscribers = list(self._subscribers)
        for websocket in subscribers:
            try:
                await websocket.send_text(data)
            except RuntimeError:
                await self.remove_subscriber(websocket)

    async def _broadcast_binary(self, data: bytes) -> None:
        async with self._lock:
            subscribers = list(self._subscribers)
        for websocket in subscribers:
            try:
                await websocket.send_bytes(data)
            except RuntimeError:
                await self.remove_subscriber(websocket)

