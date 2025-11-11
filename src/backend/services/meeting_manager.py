from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..schemas.meeting import (
    Agent,
    AgentCreate,
    Meeting,
    MeetingContextAdd,
    MeetingContextItem,
    MeetingContextRequest,
    MeetingCreate,
    MeetingParticipant,
    MeetingToolInvocation,
    MeetingToolRun,
)


@dataclass
class MeetingState:
    meeting: Meeting


class MeetingManager:
    """In-memory manager for agents, meetings, context, and tool invocations."""

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._meetings: Dict[str, MeetingState] = {}
        self._lock = asyncio.Lock()

    async def create_agent(self, payload: AgentCreate) -> Agent:
        agent = Agent(
            agent_id=self._generate_id("agent"),
            name=payload.name,
            email=payload.email,
            capabilities=payload.capabilities,
            created_at=datetime.utcnow(),
        )
        async with self._lock:
            self._agents[agent.agent_id] = agent
        return agent

    async def get_agent(self, agent_id: str) -> Agent:
        async with self._lock:
            if agent_id not in self._agents:
                raise KeyError(f"Agent {agent_id} not found")
            return self._agents[agent_id]

    async def create_meeting(self, payload: MeetingCreate) -> Meeting:
        meeting = Meeting(
            meeting_id=self._generate_id("meeting"),
            title=payload.title,
            scheduled_for=payload.scheduled_for,
            created_at=datetime.utcnow(),
            participants=[],
            context=[],
            tool_runs=[],
            av_listening=False,
        )
        async with self._lock:
            self._meetings[meeting.meeting_id] = MeetingState(meeting=meeting)
        return meeting

    async def add_participant(
        self,
        meeting_id: str,
        participant_type: str,
        participant_id: str,
        display_name: Optional[str] = None,
    ) -> Meeting:
        async with self._lock:
            state = self._get_state_locked(meeting_id)
            name = display_name
            if participant_type == "agent":
                agent = self._agents.get(participant_id)
                if agent is None:
                    raise KeyError(f"Agent {participant_id} not found")
                name = name or agent.name
            elif not name:
                raise ValueError("Display name required for user participant")
            participant = MeetingParticipant(
                participant_id=participant_id,
                participant_type=participant_type,
                display_name=name,
            )
            state.meeting.participants.append(participant)
            return state.meeting

    async def request_context(self, meeting_id: str, request: MeetingContextRequest) -> Meeting:
        async with self._lock:
            state = self._get_state_locked(meeting_id)
            state.meeting.context.append(
                MeetingContextItem(
                    context_id=self._generate_id("ctx"),
                    source_type="request",
                    payload={
                        "message": request.message,
                        "requested_by": request.requested_by,
                    },
                    added_at=request.requested_at,
                    added_by=request.requested_by,
                )
            )
            return state.meeting

    async def add_context(self, meeting_id: str, payload: MeetingContextAdd) -> Meeting:
        async with self._lock:
            state = self._get_state_locked(meeting_id)
            state.meeting.context.append(
                MeetingContextItem(
                    context_id=self._generate_id("ctx"),
                    source_type=payload.source_type,
                    payload=payload.payload,
                    added_at=datetime.utcnow(),
                    added_by=payload.added_by,
                )
            )
            return state.meeting

    async def start_av_listener(self, meeting_id: str) -> Meeting:
        async with self._lock:
            state = self._get_state_locked(meeting_id)
            state.meeting.av_listening = True
            return state.meeting

    async def run_tool(self, meeting_id: str, payload: MeetingToolInvocation) -> Meeting:
        async with self._lock:
            state = self._get_state_locked(meeting_id)
            run = MeetingToolRun(
                run_id=self._generate_id("tool"),
                tool_name=payload.tool_name,
                status="running",
                requested_at=datetime.utcnow(),
                result_summary=None,
            )
            state.meeting.tool_runs.append(run)
            return state.meeting

    async def get_meeting(self, meeting_id: str) -> Meeting:
        async with self._lock:
            state = self._meetings.get(meeting_id)
            if state is None:
                raise KeyError(f"Meeting {meeting_id} not found")
            return state.meeting

    def _get_state_locked(self, meeting_id: str) -> MeetingState:
        if meeting_id not in self._meetings:
            raise KeyError(f"Meeting {meeting_id} not found")
        return self._meetings[meeting_id]

    def _generate_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:10]}"

