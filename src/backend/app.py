from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .pipelines.video_in_video_agent import VideoInVideoAgent
from .schemas.session import SessionCreate, SessionStatus
from .services.agui_connector import AGUIConnector
from .services.session_manager import ViVSessionManager

logger = logging.getLogger(__name__)

AGUI_BASE_URL = os.environ.get("AGUI_BASE_URL", "http://localhost:5000")
AGUI_TOKEN = os.environ.get("AGUI_TOKEN")

agui_connector = AGUIConnector(AGUI_BASE_URL, token=AGUI_TOKEN)
video_agent = VideoInVideoAgent(agui_connector=agui_connector)
session_manager = ViVSessionManager(video_agent)

app = FastAPI(title="AGUI Video-in-Video Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/viv/sessions", response_model=SessionStatus, tags=["viv"])
async def create_session(payload: SessionCreate) -> SessionStatus:
    logger.info("Creating ViV session for project %s", payload.project_id)
    return await session_manager.create_session(payload)


@app.get("/viv/sessions/{session_id}", response_model=SessionStatus, tags=["viv"])
async def get_session_status(session_id: str) -> SessionStatus:
    try:
        return await session_manager.get_status(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/viv/sessions/{session_id}", status_code=202, tags=["viv"])
async def stop_session(session_id: str) -> dict[str, str]:
    try:
        await session_manager.stop_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "stopping"}


@app.websocket("/viv/streams/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str) -> None:
    try:
        await session_manager.attach_stream(session_id, websocket)
    except KeyError:
        await websocket.close(code=4004)

