## Clara Meeting Agent Overview

`clara-ai-vX@kpmg.com` is a meeting copilot focused on real-time analytics for enterprise video conferences. The agent acts as a virtual attendee that can be invited to meetings, request preparatory context from organizers, capture audio/video streams during the session, orchestrate specialized analytics tools, and project insights into a shared canvas or companion UI.

## Goals and Outcomes
- Deliver contextualized meeting intelligence (summaries, KPIs, risks, sentiment, highlights) while the meeting is in progress.
- Reduce meeting prep time by prompting hosts for relevant collateral (agendas, emails, attachments).
- Amplify participants' situational awareness via live dashboards and callouts rendered in a canvas.
- Maintain compliance for enterprise environments (access control, consent, auditable actions).

## Key Capabilities
- **Meeting invitation & authentication**: Unique agent identity (`clara-ai-vX@kpmg.com`) that can be added to calendar invites, supporting OAuth-based auth to conferencing platforms (Teams, Zoom, Meet).
- **Context ingestion**: Automated request for pre-read materials (email threads, decks, CRM notes) with secure upload and structured ingestion pipeline.
- **Multimodal capture**: Real-time access to meeting audio, video, and screen share feeds via platform SDKs with consent tracking.
- **Analytics orchestration**: Toolchain of sub-agents running specialized workloads (ASR, topic modeling, sentiment, KPI extraction, action item detection, slide parsing).
- **Canvas delivery**: Continuous publishing of insights to a shared canvas (web app or embedded panel) with versioned widgets, alerts, and drill-down links.
- **Post-meeting assets**: Generate recap package (summary, transcript excerpts, decisions, action items) stored in knowledge base with governed retention.

## System Architecture
- **Meeting Agent Service**
  - Calendar integration service (Microsoft Graph/Google Workspace).
  - Identity & consent management.
  - Meeting session controller that spins up per-meeting pipelines.
- **Context Service**
  - Context request orchestrator triggered on invite acceptance.
  - ETL pipeline to normalize email messages, attachments, CRM entities into structured context graph.
  - Secure object storage for raw artifacts.
- **Media Pipeline**
  - Real-time audio/video/screen ingestion using conferencing platform webhooks or SDK bridges.
  - Automatic speech recognition (ASR) producing live transcript segments with timestamps.
  - Video frame sampling for slide OCR and screen content tagging.
- **Analytics Orchestrator**
  - Event bus (e.g., Kafka, Redis Streams) feeds transcripts, frames, metadata to worker pool.
  - Sub-agents (pluggable microservices) implement analytics tools:
    - Topic clustering & agenda tracking.
    - Sentiment/engagement scoring.
    - KPI extraction from spoken or displayed metrics.
    - Action item & decision detection with owner assignment.
    - Compliance/risk flagging.
- **Canvas & Experience Layer**
  - Real-time canvas service (WebSocket/SignalR) updating widgets.
  - Meeting companion UI for participants to explore insights, pause analytics, provide feedback.
  - API connectors for exporting insights to CRM, task managers, knowledge bases.
- **Data & Governance**
  - Metadata store indexing meetings, participants, consent, analytics outputs.
  - Audit logging for tool invocations and data access.
  - Policy engine enforcing retention, redaction, tenant isolation.

## Core Workflows
1. **Agent Invitation & Setup**
   - Organizer invites `clara-ai-vX@kpmg.com` via calendar.
   - Agent verifies organizer authorization, registers meeting metadata, and issues context request email with secure upload link.

2. **Context Collection**
   - Organizer uploads agenda, prior emails, attachments.
   - Context service parses content, extracts entities (clients, KPIs), and tags them against meeting.
   - Summary digest prepared for quick pre-read.

3. **Meeting Execution**
   - Upon meeting start, agent joins via conferencing SDK.
   - Consent banner displayed; agent respects regional compliance settings.
   - Media pipeline streams audio/video/screen share to ASR and vision sub-agents.
   - Live transcript segments push onto event bus.
   - Sub-agents consume events, produce analytics payloads (topics, insights, anomalies).
   - Canvas layer renders widgets (e.g., trend charts, action item lists) and updates in near real-time.

4. **Participant Interaction**
   - Users can query Clara via chat for clarifications.
   - Agent can request missing context or flag off-topic discussions referencing prep materials.
   - Facilitator can pause/resume analytics or hide sensitive widgets.

5. **Post-Meeting Wrap-Up**
   - Agent compiles highlights, decisions, action items, transcript snippets.
   - Deliverables emailed to participants, synced to knowledge base, and optionally pushed to CRM/task tools.
   - Meeting artifacts stored with retention policy and access controls.

## Tooling & Sub-Agent Design
- Sub-agents communicate via analytics orchestrator contracts (input schema, output schema).
- Each sub-agent can be upgraded independently; orchestrator handles routing and retries.
- Example sub-agents:
  - `speech-topic-tool`: BERT-based topic extraction to monitor agenda coverage.
  - `sentiment-tool`: Transformer scoring participant sentiment & engagement.
  - `metric-vision-tool`: Detect numeric KPIs from screen captures using OCR + NLP.
  - `action-item-tool`: Prompted LLM generating structured tasks with owners/dates.
  - `compliance-monitor`: Rule-based flags for restricted language or data leaks.
- Tools can respond with UI widget descriptors (charts, tables) which the canvas service renders.

## Integration Considerations
- **Platforms**: Initial focus on Microsoft Teams (Graph API, Teams bot), with adapters for Zoom and Google Meet.
- **Security**: Enterprise SSO, consent management, encryption at rest/in transit, redaction workflows.
- **Scalability**: Horizontal scaling of media processing and analytics workers; use autoscaling triggers on meeting load.
- **Extensibility**: Plugin framework for client-specific analytics modules; declarative configuration per engagement.

## Implementation Roadmap
1. **MVP**
   - Calendar invitation handler & context request workflow.
   - Audio-only pipeline with ASR and live transcript.
   - Basic analytics sub-agent (action items, summary).
   - Canvas UI with transcript feed and action item list.
2. **Phase 2**
   - Video/screen ingestion, slide parsing, KPI detection.
   - Sentiment analytics, agenda tracking, chat Q&A interface.
   - Data governance controls (consent, audit logs).
3. **Phase 3**
   - Custom analytics marketplace (client-specific plugins).
   - Predictive insights (risks, next-best actions).
   - Deep integrations with CRM, task systems, and knowledge graph.

## Open Questions
- Target conferencing platform priority and available SDK access?
- Data residency/compliance requirements for KPMG tenants?
- Preferred canvas implementation (embedded in meeting client vs external web app)?
- Required SLAs for real-time analytics latency and accuracy thresholds?
