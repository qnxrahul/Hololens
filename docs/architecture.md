## Video-in-Video AI Agent for AGUI Data Analyzer with HoloLens

### 1. Goals & Scope
- Extend the existing AGUI data analyzer so that analysts can inspect live or recorded media feeds while remaining inside the AGUI workflow.
- Introduce **video-in-video (ViV)** capabilities: display an analyzed sub-stream inside the primary video feed with AI-driven overlays (detections, annotations, metrics).
- Surface the augmented video inside a HoloLens 2 experience, enabling spatial placement, hands-free control, and contextual data exploration.
- Maintain modularity so the ViV agent can run on-edge or in the cloud, and communicate with the AGUI data analyzer via standard APIs.

### 2. High-Level Architecture

```
+----------------+        +----------------------+        +-----------------+
| AGUI Data      |        | ViV AI Agent Service |        | HoloLens Client |
| Analyzer Core  | <----> |  (FastAPI / gRPC)    | <----> |  (Unity + MRTK) |
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
   - Streams the augmented output to subscribers (HoloLens client, AGUI web UI).
   - Persists derived analytics back into AGUI via its REST/gRPC endpoints.

3. **HoloLens Client**  
   Built with Unity + MRTK 3. Consumes the WebRTC/WebSocket stream from the agent, renders it on a floating slate or pinned to world anchors, and projects controls (pause, zoom, timeline scrub, model selection). Provides voice/gesture commands that are forwarded to the agent.

### 3. Data & Control Flow

1. **Session Request**  
   - An AGUI operator selects a dataset/video and enables ViV analysis.
   - AGUI issues `POST /viv/sessions` with metadata (video URI, desired models, output format, HoloLens consumer ID).

2. **Stream Preparation**  
   - ViV agent fetches or subscribes to the video source (RTSP, MP4, live feed).
   - Frames enter the **Inference Pipeline** (preprocessing → model inference → post-processing).

3. **Composite Rendering**  
   - `VideoComposer` blends the base stream with the insight sub-stream (cropped ROI, zoomed track, or 3D overlay).
   - Overlay metadata (detections, KPIs) packaged as JSON frame annotations.

4. **Delivery**  
   - Augmented frames and annotations published over WebRTC/DataChannel or HLS for low latency consumption.
   - HoloLens client subscribes, displays the composited video, and visualizes metrics as holographic widgets.
   - User interactions (gestures, gaze-based selection, voice commands) travel back via WebSocket control channel to adjust the analysis (ROI, thresholds, model swap).

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
| `HoloLensClient`         | Render stream, manage spatial UI, relay user input | Unity, MRTK 3, MixedReality-WebRTC |
| `AGUIConnector`          | Auth, fetch datasets, push results | `requests`, websockets |

### 5. Deployment Topologies

- **Edge Appliance**: ViV agent runs on-prem with GPU; HoloLens connects via local Wi-Fi; AGUI orchestrator co-located.
- **Hybrid Cloud**: ViV inference pipeline hosted in Azure; AGUI on cloud with secure tunnels; HoloLens connects over internet with Azure AD auth.
- **Failover / Offline**: Cache AGUI datasets and allow local-only inference when connection drops. Sync results once connectivity resumes.

### 6. Security & Compliance
- Use OAuth2/OIDC tokens from AGUI identity provider; short-lived session tokens for HoloLens.
- Encrypt transport via DTLS/SRTP (WebRTC) or HTTPS.
- Enforce role-based access (analyst vs. admin) for model configuration and data export.
- Log inference decisions and interactions for audit (GDPR/ITAR considerations).

### 7. Performance Considerations
- Target <150 ms end-to-end latency for live feeds (HoloLens comfortable threshold).
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
- Preferred protocol for HoloLens streaming (WebRTC vs. HLS vs. RTMP).
- Model selection: should it reuse AGUI’s existing model registry or maintain an agent-specific catalog?

### 10. Frontend Dashboard Overview
- React + Vite + Tailwind SPA, hosted under `src/frontend`, provides ViV session lifecycle controls and monitoring.
- Uses REST endpoints (`/viv/sessions`) via React Query for creation, status polling, and termination.
- Consumes WebSocket stream `/viv/streams/{sessionId}` to render live video (JPEG placeholder) and insight metadata.
- Shares authentication context with AGUI (OAuth token injection) and targets desktop/tablet form factors.
- Detailed UX and component breakdown in `docs/frontend-architecture.md`.

