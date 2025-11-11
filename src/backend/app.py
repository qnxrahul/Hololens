from __future__ import annotations

import logging
import os

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from .pipelines.video_in_video_agent import VideoInVideoAgent
from .schemas.session import SessionCreate, SessionStatus
from .schemas.media import MediaItem
from .schemas.meeting import (
    Agent,
    AgentCreate,
    Meeting,
    MeetingContextAdd,
    MeetingContextRequest,
    MeetingCreate,
    MeetingToolInvocation,
)
from .services.auth import JWKSAuthenticator, JWKSSettings
from .services.agui_connector import AGUIConnector
from .services.session_manager import ViVSessionManager
from .services.meeting_manager import MeetingManager
from .services.storage import LocalStorageClient, LocalStorageSettings

logger = logging.getLogger(__name__)

AGUI_BASE_URL = os.environ.get("AGUI_BASE_URL", "http://localhost:5000")
AGUI_TOKEN = os.environ.get("AGUI_TOKEN")

AUTH_JWKS_URL = os.environ.get("AUTH_JWKS_URL")
AUTH_AUDIENCE = os.environ.get("AUTH_AUDIENCE")
AUTH_ISSUER = os.environ.get("AUTH_ISSUER")

STORAGE_ROOT = os.environ.get("STORAGE_ROOT", "/tmp/viv-media")
STORAGE_BASE_URL = os.environ.get("STORAGE_BASE_URL", "/media")

authenticator: Optional[JWKSAuthenticator] = None
if AUTH_JWKS_URL:
    authenticator = JWKSAuthenticator(
        JWKSSettings(jwks_url=AUTH_JWKS_URL, audience=AUTH_AUDIENCE, issuer=AUTH_ISSUER)
    )

storage_client = LocalStorageClient(
    LocalStorageSettings(root=Path(STORAGE_ROOT), base_url=STORAGE_BASE_URL)
)

agui_connector = AGUIConnector(AGUI_BASE_URL, token=AGUI_TOKEN)
video_agent = VideoInVideoAgent(agui_connector=agui_connector, storage=storage_client)
session_manager = ViVSessionManager(video_agent)
meeting_manager = MeetingManager()

bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(title="AGUI Video-in-Video Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    try:
        storage_client.ensure_ready()
    except Exception as exc:  # pragma: no cover - filesystem issues
        logger.warning("Unable to ensure storage root: %s", exc)


async def require_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    if authenticator is None:
        if credentials:
            logger.debug("Authorization header supplied but authenticator disabled")
        return {"sub": "anonymous"}
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        return await authenticator.verify_token(credentials.credentials)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/agents",
    response_model=Agent,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def create_agent(payload: AgentCreate) -> Agent:
    return await meeting_manager.create_agent(payload)


@app.post(
    "/meetings",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def create_meeting(payload: MeetingCreate) -> Meeting:
    return await meeting_manager.create_meeting(payload)


@app.post(
    "/meetings/{meeting_id}/participants",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def add_participant(
    meeting_id: str,
    participant_type: str,
    participant_id: str,
    display_name: Optional[str] = None,
) -> Meeting:
    return await meeting_manager.add_participant(
        meeting_id,
        participant_type=participant_type,
        participant_id=participant_id,
        display_name=display_name,
    )


@app.post(
    "/meetings/{meeting_id}/context/request",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def request_meeting_context(meeting_id: str, payload: MeetingContextRequest) -> Meeting:
    return await meeting_manager.request_context(meeting_id, payload)


@app.post(
    "/meetings/{meeting_id}/context",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def add_meeting_context(meeting_id: str, payload: MeetingContextAdd) -> Meeting:
    return await meeting_manager.add_context(meeting_id, payload)


@app.post(
    "/meetings/{meeting_id}/av/start",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def start_meeting_av(meeting_id: str) -> Meeting:
    return await meeting_manager.start_av_listener(meeting_id)


@app.post(
    "/meetings/{meeting_id}/tools/run",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def run_meeting_tool(meeting_id: str, payload: MeetingToolInvocation) -> Meeting:
    return await meeting_manager.run_tool(meeting_id, payload)


@app.get(
    "/meetings/{meeting_id}",
    response_model=Meeting,
    tags=["meetings"],
    dependencies=[Depends(require_user)],
)
async def get_meeting(meeting_id: str) -> Meeting:
    return await meeting_manager.get_meeting(meeting_id)


@app.post(
    "/viv/sessions",
    response_model=SessionStatus,
    tags=["viv"],
    dependencies=[Depends(require_user)],
)
async def create_session(payload: SessionCreate) -> SessionStatus:
    logger.info("Creating ViV session for project %s", payload.project_id)
    return await session_manager.create_session(payload)


@app.get(
    "/viv/sessions/{session_id}",
    response_model=SessionStatus,
    tags=["viv"],
    dependencies=[Depends(require_user)],
)
async def get_session_status(session_id: str) -> SessionStatus:
    try:
        return await session_manager.get_status(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete(
    "/viv/sessions/{session_id}",
    status_code=202,
    tags=["viv"],
    dependencies=[Depends(require_user)],
)
async def stop_session(session_id: str) -> dict[str, str]:
    try:
        await session_manager.stop_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "stopping"}


@app.get(
    "/viv/sessions/{session_id}/media",
    response_model=List[MediaItem],
    tags=["viv"],
    dependencies=[Depends(require_user)],
)
async def list_session_media(session_id: str) -> List[MediaItem]:
    entries = storage_client.list_media(f"{session_id}/")
    return [MediaItem(**entry) for entry in entries]


@app.websocket("/viv/streams/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str) -> None:
    if authenticator:
        token = websocket.query_params.get("token")
        if not token:
            authorization = websocket.headers.get("authorization")
            if authorization and authorization.lower().startswith("bearer "):
                token = authorization.split(" ", 1)[1]
        if not token:
            await websocket.close(code=4401)
            return
        try:
            await authenticator.verify_token(token)
        except PermissionError:
            await websocket.close(code=4403)
            return

    try:
        await session_manager.attach_stream(session_id, websocket)
    except KeyError:
        await websocket.close(code=4004)


app.mount(
    STORAGE_BASE_URL.rstrip("/") or "/media",
    StaticFiles(directory=Path(STORAGE_ROOT), check_dir=False),
    name="media",
)

