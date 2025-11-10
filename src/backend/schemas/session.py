from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration payload for selecting AI models within a session."""

    name: str = Field(..., description="Identifier of the inference model to load")
    version: Optional[str] = Field(
        None, description="Optional semantic version or commit hash of the model"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary inference parameters (thresholds, ROI, etc.)",
    )


class VideoWindow(BaseModel):
    """Defines the placement and purpose of an inset video in the composite output."""

    label: str = Field(..., description="Human-friendly label shown on HUD overlays")
    relative_position: Dict[str, float] = Field(
        default_factory=lambda: {"x": 0.72, "y": 0.05},
        description="Top-left anchor of the inset window relative to frame size (0-1)",
    )
    relative_size: Dict[str, float] = Field(
        default_factory=lambda: {"width": 0.25, "height": 0.25},
        description="Size of the inset window relative to frame size (0-1)",
    )


class SessionCreate(BaseModel):
    """Client request for launching a new ViV session."""

    project_id: str = Field(..., description="AGUI project/data analyzer identifier")
    source_uri: str = Field(
        ...,
        description="URI to media stream (rtsp/http/file) or AGUI asset identifier",
    )
    consumer_device_id: Optional[str] = Field(
        default=None,
        description="Optional device identifier (e.g., HoloLens spatial anchor ID)",
    )
    models: List[ModelConfig] = Field(
        default_factory=list,
        description="List of inference models to activate for this session",
    )
    video_window: VideoWindow = Field(
        default_factory=VideoWindow,
        description="Placement of the inset video and overlays",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Free-form metadata forwarded to AGUI"
    )


class SessionStatus(BaseModel):
    """State returned to clients regarding a ViV session."""

    session_id: str
    state: str = Field(description="Lifecycle state, e.g. initializing/running/stopped")
    started_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    stream_endpoint: Optional[str] = Field(
        default=None, description="WebRTC or HLS endpoint for the augmented stream"
    )


class InsightEvent(BaseModel):
    """Analytics emitted by the ViV agent back into AGUI."""

    session_id: str
    timestamp: datetime
    payload: Dict[str, Any]

