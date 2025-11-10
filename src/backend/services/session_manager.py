from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from fastapi import WebSocket

from ..pipelines.video_in_video_agent import SessionContext, VideoInVideoAgent
from ..schemas.session import SessionCreate, SessionStatus
from .insight_publisher import InsightPublisher


class SessionState(str, Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass
class SessionRecord:
    context: SessionContext
    state: SessionState = SessionState.INITIALIZING
    started_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)
    task: Optional[asyncio.Task] = None
    error: Optional[str] = None


class ViVSessionManager:
    """Lifecycle management for ViV sessions."""

    def __init__(self, agent: VideoInVideoAgent) -> None:
        self._agent = agent
        self._sessions: Dict[str, SessionRecord] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, payload: SessionCreate) -> SessionStatus:
        session_id = self._generate_session_id()
        publisher = InsightPublisher()
        context = SessionContext(session_id=session_id, config=payload, publisher=publisher)
        record = SessionRecord(context=context)

        async with self._lock:
            self._sessions[session_id] = record

        record.task = asyncio.create_task(self._run_session(record))
        return self._build_status(record)

    async def attach_stream(self, session_id: str, websocket: WebSocket) -> None:
        record = await self._get_record(session_id)
        await record.context.publisher.add_subscriber(websocket)
        try:
            while True:
                await websocket.receive_text()
        except Exception:
            pass
        finally:
            await record.context.publisher.remove_subscriber(websocket)

    async def stop_session(self, session_id: str) -> None:
        record = await self._get_record(session_id)
        if record.task and not record.task.done():
            record.task.cancel()
        record.state = SessionState.STOPPED
        record.updated_at = datetime.utcnow()

    async def get_status(self, session_id: str) -> SessionStatus:
        record = await self._get_record(session_id)
        return self._build_status(record)

    async def _run_session(self, record: SessionRecord) -> None:
        record.state = SessionState.RUNNING
        record.started_at = datetime.utcnow()
        record.updated_at = datetime.utcnow()
        try:
            await self._agent.run_session(record.context, max_frames=record.context.config.metadata.get("max_frames"))
            record.state = SessionState.STOPPED
        except asyncio.CancelledError:
            record.state = SessionState.STOPPED
            raise
        except Exception as exc:  # pragma: no cover - runtime error path
            record.state = SessionState.FAILED
            record.error = str(exc)
        finally:
            record.updated_at = datetime.utcnow()

    async def _get_record(self, session_id: str) -> SessionRecord:
        async with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Session {session_id} not found.")
            return self._sessions[session_id]

    def _build_status(self, record: SessionRecord) -> SessionStatus:
        return SessionStatus(
            session_id=record.context.session_id,
            state=record.state.value,
            started_at=record.started_at,
            updated_at=record.updated_at,
            stream_endpoint=f"/viv/streams/{record.context.session_id}",
        )

    def _generate_session_id(self) -> str:
        return datetime.utcnow().strftime("viv-%Y%m%d%H%M%S-%f")

