## Video-in-Video AI Agent for AGUI Data Analyzer with WebXR

### 1. Goals & Scope
- Extend the existing AGUI data analyzer so that analysts can inspect live or recorded media feeds while remaining inside the AGUI workflow.
- Introduce **video-in-video (ViV)** capabilities: display an analyzed sub-stream inside the primary video feed with AI-driven overlays (detections, annotations, metrics).
- Surface the augmented video inside WebXR-enabled browsers (Chrome/Edge) so users with headsets or AR-capable devices can experience spatial visualization without native apps.
- Maintain modularity so the ViV agent can run on-edge or in the cloud, and communicate with the AGUI data analyzer via standard APIs.

### 2. High-Level Architecture

```
+----------------+        +----------------------+        +-----------------+
| AGUI Data      |        | ViV AI Agent Service |        | Web XR Client   |
| Analyzer Core  | <----> |  (FastAPI / gRPC)    | <----> |  (React + WebXR)|
| (Python)       |        |                      |        |                 |
+----------------+        +-----------+----------+        +---------+-------+
                                      |                             |
                                      v                             v
                             +-----------------+         +---------------------+
                             | AI Inference    |         | Spatial Presentation |
                             | Pipeline (Py)   |         | & Interaction (C#)  |
                             +-----------------+         +---------------------+
```

1. **AGUI Data Analyzer Core**  
   Provides project metadata, datasets, annotations, and analytics APIs (`/projects`, `/insights`, `/signals`, etc.). It publishes events when a user requests ViV processing.

2. **ViV AI Agent Service**  
   A Python service (FastAPI + WebSockets) that:
   - Pulls raw video frames or stream URLs from AGUI.
   - Runs the AI inference pipeline (object/action detection, segmentation, etc.).
   - Composites a secondary "insight video" onto the base stream (video-in-video) together with overlays (bounding boxes, heatmaps, metric HUD).
    - Streams the augmented output to subscribers (Web dashboard, WebXR immersive view).
    - Hosts meeting orchestration APIs for agent creation, context collection, tool requests, and AV lifecycle events.
   - Persists derived analytics back into AGUI via its REST/gRPC endpoints.

3. **WebXR Client**  
   Built with React + `@react-three/xr`. Consumes the WebRTC/WebSocket stream from the agent, renders it on a floating canvas within immersive or AR scenes, and provides controls (pause, zoom, timeline scrub, model selection). Uses standard web inputs (controllers, gaze, keyboard) to adjust analysis parameters.

### 3. Data & Control Flow

1. **Session Request**  
   - An AGUI operator selects a dataset/video and enables ViV analysis.
    - AGUI issues `POST /viv/sessions` with metadata (video URI, desired models, output format, WebXR consumer context).

2. **Stream Preparation**  
   - ViV agent fetches or subscribes to the video source (RTSP, MP4, live feed).
   - Frames enter the **Inference Pipeline** (preprocessing → model inference → post-processing).

3. **Composite Rendering**  
   - `VideoComposer` blends the base stream with the insight sub-stream (cropped ROI, zoomed track, or 3D overlay).
   - Overlay metadata (detections, KPIs) packaged as JSON frame annotations.

4. **Delivery**  
   - Augmented frames and annotations published over WebRTC/DataChannel or HLS for low latency consumption.
    - WebXR client subscribes, displays the composited video, and visualizes metrics as holographic widgets.
    - User interactions (controllers, gaze-based selection, voice commands) travel back via WebSocket control channel to adjust the analysis (ROI, thresholds, model swap).
    - Composite frames optionally persisted to local media storage and exposed via REST for later review or export.
    - Agents can trigger meeting tool runs whose outputs are rendered into the collaborative canvas.

5. **Feedback Loop**  
   - AI insights persisted back into AGUI (events, derived datasets, timeline markers).
   - AGUI UI updates dashboards, enabling collaborative review or downstream automation.

### 4. Components Detail

| Component                | Key Responsibilities | Technologies |
|--------------------------|----------------------|--------------|
| `FrameIngestor`          | Retrieve frames from URI or AGUI data store; handle buffering and format normalization | OpenCV / FFmpeg |
| `InferenceOrchestrator`  | Manage AI models (ONNX, Torch), batch frames, run GPU/CPU inference | ONNX Runtime, PyTorch |
| `VideoComposer`          | Create picture-in-picture layout, draw overlays, encode output stream | OpenCV, PyAV |
| `InsightPublisher`       | Stream video + metadata, expose REST for session control | FastAPI, WebRTC (aiortc) |
| `WebXRClient`            | Render stream, manage spatial UI, relay user input | React, WebXR, Three.js |
| `AGUIConnector`          | Auth, fetch datasets, push results | `requests`, websockets |
| `MeetingManager`         | Manage agents, meeting lifecycle, context, and tool invocations | FastAPI, in-memory state (extensible to DB) |

### 5. Deployment Topologies

- **Edge Appliance**: ViV agent runs on-prem with GPU; Web clients connect via local Wi-Fi; AGUI orchestrator co-located.
- **Hybrid Cloud**: ViV inference pipeline hosted in Kubernetes (e.g., k3s/microk8s/K8s) with S3-compatible storage (Ceph, MinIO) and Keycloak for auth; secure tunnels connect remote analysts.
- **Failover / Offline**: Cache AGUI datasets and allow local-only inference when connection drops. Sync results once connectivity resumes.

### 6. Security & Compliance
- Use OAuth2/OIDC tokens from an open-source IdP (Keycloak, Authentik) with JWKS validation in the agent; short-lived session tokens for WebXR/Web clients.
- Encrypt transport via DTLS/SRTP (WebRTC) or HTTPS.
- Enforce role-based access (analyst vs. admin) for model configuration and data export.
- Log inference decisions and interactions for audit (GDPR/ITAR considerations).

### 7. Performance Considerations
- Target <150 ms end-to-end latency for live feeds (comfortable threshold for immersive viewing).
- Adaptive bitrate on output stream to accommodate wireless network variability.
- GPU scheduling for multiple concurrent sessions; degrade gracefully (switch to key insights vs. full PiP).
- Offline batch mode to precompute overlays for recorded sessions.

### 8. Extensibility & Future Work
- Plug-in architecture for additional models (pose estimation, anomaly detection).
- Multi-view support: multiple insight tiles inside primary video.
- Integration with AGUI collaborative annotations (shared cursors, notes).
- Support for cross-device experiences (desktop web, iPad) using the same ViV stream.

### 9. Key Open Questions
- Exact AGUI API contracts for pulling video and pushing insights.
- Preferred protocol for immersive streaming (WebRTC vs. HLS vs. RTMP).
- Model selection: should it reuse AGUI’s existing model registry or maintain an agent-specific catalog?

### 10. Frontend Dashboard Overview
- React + Vite + Tailwind SPA, hosted under `src/frontend`, provides ViV session lifecycle controls and monitoring.
- Uses REST endpoints (`/viv/sessions`) via React Query for creation, status polling, and termination.
- Consumes WebSocket / WebRTC stream `/viv/streams/{sessionId}` to render live video (JPEG placeholder) and insight metadata.
- Offers optional WebXR immersive view (Chrome WebXR) via Three.js canvas that projects the video stream in 3D space.
- Shares authentication context with AGUI/Keycloak (OAuth token injection) and targets desktop/tablet form factors.
- Detailed UX and component breakdown in `docs/frontend-architecture.md`.

### 11. Storage & Media Handling
- Filesystem-backed media store (`STORAGE_ROOT`) for session artifacts, recorded frames, and exported reports (suitable for local or on-prem deployments).
- Optional migration path: swap in an S3-compatible open-source backend (MinIO, Ceph RGW) by adapting the storage client.
- HTTP-serving of stored media via FastAPI static mount (`/media`), keeping assets behind the same auth context.
- Optional message bus (NATS/Kafka) for downstream analytics or asynchronous notification pipelines.

