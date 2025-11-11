from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class AgentCreate(BaseModel):
    name: str = Field(..., description="Display name for the agent")
    email: EmailStr
    capabilities: List[str] = Field(
        default_factory=list, description="Declared tool or domain capabilities"
    )


class Agent(BaseModel):
    agent_id: str
    name: str
    email: EmailStr
    capabilities: List[str]
    created_at: datetime


class MeetingCreate(BaseModel):
    title: str
    scheduled_for: Optional[datetime] = None


class MeetingParticipant(BaseModel):
    participant_id: str
    participant_type: str = Field(..., regex="^(agent|user)$")
    display_name: str


class MeetingContextItem(BaseModel):
    context_id: str
    source_type: str = Field(..., description="e.g., email, agenda, document")
    payload: Dict[str, str]
    added_at: datetime
    added_by: str


class MeetingToolRun(BaseModel):
    run_id: str
    tool_name: str
    status: str
    requested_at: datetime
    result_summary: Optional[str] = None


class Meeting(BaseModel):
    meeting_id: str
    title: str
    scheduled_for: Optional[datetime] = None
    created_at: datetime
    participants: List[MeetingParticipant]
    context: List[MeetingContextItem]
    tool_runs: List[MeetingToolRun]
    av_listening: bool = False


class MeetingContextRequest(BaseModel):
    requested_by: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    message: str = Field(
        default="Please provide relevant meeting context (e.g., emails, documents, agenda)."
    )


class MeetingContextAdd(BaseModel):
    source_type: str
    payload: Dict[str, str]
    added_by: str


class MeetingToolInvocation(BaseModel):
    tool_name: str
    parameters: Dict[str, str] = Field(default_factory=dict)
    requested_by: str

