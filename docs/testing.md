## Testing & Verification Strategy

### 1. Backend
- **Unit Tests** (`pytest`):
  ```bash
  pip install -r requirements-dev.txt
  pytest
  ```
- **Manual API Smoke Test**:
  1. Launch FastAPI: `uvicorn src.backend.app:app --reload`.
  2. Create a session:
     ```bash
     curl -X POST http://localhost:8001/viv/sessions \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer <token>" \
       -d '{"project_id":"demo","source_uri":"rtsp://camera","metadata":{"max_frames":10}}'
     ```
  3. Stream frames with a WebSocket client and verify `/viv/sessions/{id}/media` returns stored snapshots.

- **Media Serving**: Access `http://localhost:8001/media/<session_id>/frames/frame_000000.jpg` to ensure static hosting works.

### 2. Frontend
- **Type Check & Lint**:
  ```bash
  cd src/frontend
  npm install
  npm run typecheck
  npm run lint
  ```
- **Development Server**:
  ```bash
  npm run dev
  ```
  - Paste a bearer token via the **Auth Token** widget.
  - Start a session and confirm:
    - Stream renders in the viewer.
    - WebXR button enters immersive mode on supported devices.
    - Metadata feed and saved media list update in near real time.

### 3. End-to-End
- Configure a sample RTSP/MP4 source (e.g., `ffmpeg` loop) to simulate live video.
- Run backend + frontend, start a session, verify snapshots saved under `STORAGE_ROOT` and accessible via `/media`.
- Optional: automate via playwright + pytest by scripting WebSocket ingestion and REST calls.
