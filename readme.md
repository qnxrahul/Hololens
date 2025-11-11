## AGUI Video-in-Video AI Agent

This repository contains a scaffold for extending the [AGUI data analyzer](https://github.com/ag-ui-protocol/ag-ui) with a **video-in-video (ViV) AI agent** that streams augmented insights to both standard browsers and WebXR immersive experiences.

### Key Features
- FastAPI backend orchestrating video ingestion, AI inference, and picture-in-picture composition.
- Pluggable inference orchestrator with a debug backend (grayscale) and hooks for ONNX/PyTorch models.
- WebSocket/WebRTC stream for delivering augmented frames and metadata to browser clients.
- React dashboard with WebXR support (Chrome/Edge) for immersive visualization alongside traditional 2D monitoring.
- Documentation describing architecture, deployment, and open integration questions.

### Project Structure

```
docs/architecture.md          # System design and integration overview
docs/frontend-architecture.md # Frontend UX and WebXR notes
src/backend/app.py            # FastAPI entry point
src/backend/services/         # Frame ingestion, inference, AGUI connector, auth, storage
src/backend/pipelines/        # Video-in-video orchestration logic
src/frontend/                 # React dashboard with WebXR immersive mode
tests/                        # Pytest-based unit tests
requirements(.txt)            # Python dependencies
requirements-dev.txt          # Development/testing dependencies
```

### Getting Started (Backend)
1. Create a Python environment (3.10+ recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # optional, for running tests
   ```
3. Configure environment variables:
   - `AGUI_BASE_URL`: Base URL for the AGUI data analyzer APIs (default `http://localhost:5000`).
   - `AGUI_TOKEN`: Bearer token for authenticating with AGUI (optional for unauthenticated setups).
   - `AUTH_JWKS_URL`: JWKS endpoint from your identity provider (Keycloak/Authentik) for token verification.
   - `AUTH_AUDIENCE` / `AUTH_ISSUER`: Expected audience and issuer values for OAuth2 access tokens.
   - `STORAGE_ROOT`: Filesystem directory used for storing media assets (default `/tmp/viv-media`).
   - `STORAGE_BASE_URL`: URL prefix where media is exposed (default `/media`).
4. Launch the agent:
   ```bash
   uvicorn src.backend.app:app --host 0.0.0.0 --port 8001 --reload
   ```
5. Create a ViV session via REST:
   ```bash
   curl -X POST http://localhost:8001/viv/sessions \
     -H "Content-Type: application/json" \
     -d '{
           "project_id": "demo-project",
           "source_uri": "rtsp://camera/stream",
           "metadata": {"max_frames": 100},
           "video_window": {"label": "Focus", "relative_position": {"x": 0.65, "y": 0.05}}
         }'
   ```
6. Connect a WebSocket client to receive augmented frames:
   ```
   ws://localhost:8001/viv/streams/<session_id>
   ```

> **Note:** The current scaffold emits JPEG frames over WebSockets for rapid prototyping. For production low-latency streaming, replace this mechanism with WebRTC (`aiortc`) or HLS.

### Frontend Dashboard
1. Install Node.js 18+ and pnpm/npm.
2. Set up the dashboard:
   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```
3. Env vars (via `.env`):
   - `VITE_API_BASE_URL` (defaults to `http://localhost:8001`)
   - `VITE_STREAM_BASE_URL` (defaults to websocket URL derived from API base)
    - `VITE_AUTH_TOKEN_KEY` (browser storage key where the SPA reads OAuth tokens)
4. The UI provides:
   - Session creation form (project/source/model).
   - Session list with status polling and stop/remove controls.
   - Live stream viewer, Chrome WebXR immersive button, and insight metadata feed.

### WebXR Immersive Mode
- Enable Chrome WebXR flags if required (e.g., `chrome://flags/#webxr-incubations`).
- Load the dashboard, start a session, and click **Open WebXR** to enter immersive mode within a supported headset.
- Use controllers or keyboard/mouse to interact with the floating video canvas and overlays.

### Running Tests
```
pytest
```

### Next Steps
- Implement real inference backends by integrating ONNX Runtime or PyTorch models inside `InferenceOrchestrator`.
- Replace the placeholder JPEG streaming with WebRTC for efficient transmission to immersive browsers.
- Extend the AGUI connector with real authentication flows and insight schemas that match the production analyzer.
- Add telemetry, observability, and CI/CD pipelines tailored to your deployment environment.
- Fuse AGUI authentication and embed the ViV dashboard inside AGUI’s layout or kiosk mode for analysts.
- Evaluate WebXR ergonomics (depth cues, interaction) and consider porting to AR mode (`immersive-ar`) once Chrome flags stabilize.
- Extend storage workflows (versioning, cleanup) or swap in MinIO/Ceph when scaling beyond local filesystem.
- Integrate a full OIDC login (Keycloak) flow in the SPA to mint and refresh tokens automatically.
