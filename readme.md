## AGUI Video-in-Video AI Agent

This repository contains a scaffold for extending the [AGUI data analyzer](https://github.com/ag-ui-protocol/ag-ui) with a **video-in-video (ViV) AI agent** that streams augmented insights to a HoloLens 2 experience.

### Key Features
- FastAPI backend orchestrating video ingestion, AI inference, and picture-in-picture composition.
- Pluggable inference orchestrator with a debug backend (grayscale) and hooks for ONNX/PyTorch models.
- WebSocket stream for delivering augmented frames and metadata to AGUI clients and HoloLens.
- Unity/MRTK scaffold (`ViVSessionController.cs`) for consuming ViV streams, rendering them in 3D, and sending voice/gesture commands.
- React dashboard with WebXR support (Chrome) for immersive visualization alongside traditional 2D monitoring.
- Documentation describing architecture, deployment, and open integration questions.

### Project Structure

```
docs/architecture.md          # System design and integration overview
src/backend/app.py            # FastAPI entry point
src/backend/services/         # Frame ingestion, inference, AGUI connector, streaming
src/backend/pipelines/        # Video-in-video orchestration logic
src/hololens/ViVSessionController.cs  # Unity script for HoloLens client
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
4. The UI provides:
   - Session creation form (project/source/model).
   - Session list with status polling and stop/remove controls.
   - Live stream viewer, Chrome WebXR immersive button, and insight metadata feed.

### HoloLens Integration
- Import `src/hololens/ViVSessionController.cs` into a Unity project configured with MRTK 3 and MixedReality-WebRTC (or Unity WebRTC).
- Provide an implementation of the `IWebRTCClient` interface that pairs with the backend's signaling.
- Deploy to HoloLens, assign the script to a slate or quad, and map MRTK buttons to `pause/resume` commands.

### Running Tests
```
pytest
```

### Next Steps
- Implement real inference backends by integrating ONNX Runtime or PyTorch models inside `InferenceOrchestrator`.
- Replace the placeholder JPEG streaming with WebRTC for efficient transmission to the HoloLens.
- Extend the AGUI connector with real authentication flows and insight schemas that match the production analyzer.
- Add telemetry, observability, and CI/CD pipelines tailored to your deployment environment.
- Fuse AGUI authentication and embed the ViV dashboard inside AGUI’s layout or kiosk mode for analysts.
- Evaluate WebXR ergonomics (depth cues, interaction) and consider porting to AR mode (`immersive-ar`) once Chrome flags stabilize.
