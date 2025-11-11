## Frontend Dashboard Setup & Integration

### 1. Prerequisites
- Node.js 18 or later
- pnpm or npm (v8+)
- Running instance of the ViV FastAPI backend (`uvicorn src.backend.app:app`)

### 2. Installation
```bash
cd src/frontend
npm install
```

### 3. Environment Configuration
Create `.env` (or `.env.local`) in `src/frontend`:
```
VITE_API_BASE_URL=http://localhost:8001
VITE_STREAM_BASE_URL=ws://localhost:8001
```

- `VITE_API_BASE_URL`: REST endpoints for session lifecycle.
- `VITE_STREAM_BASE_URL`: WebSocket endpoint streaming JPEG frames/metadata (omit to auto-derive from window origin).
- Reuse AGUI OAuth tokens by wiring them into Axios interceptors (e.g., read from `localStorage` and set `Authorization` header).

### 4. Development Workflow
```bash
npm run dev
```
- Opens dashboard on `http://localhost:5173`.
- Hot reload when React components change.
- Chrome users with WebXR hardware can open the immersive viewer via **Open WebXR**; ensure `chrome://flags/#webxr-incubations` is enabled for AR features if needed.

### 5. Production Build
```bash
npm run build
npm run preview  # optional local smoke test
```
- Outputs to `dist/`, ready for static hosting.
- To serve via FastAPI, mount `StaticFiles`:
  ```python
  from fastapi.staticfiles import StaticFiles
  app.mount("/dashboard", StaticFiles(directory="src/frontend/dist", html=True), name="frontend")
  ```

### 6. Integration Notes
- Ensure CORS on backend includes dashboard origin.
- Embed dashboard into AGUI via iframe or reverse proxy for seamless analyst experience.
- When migrating to WebRTC, extend `useWebSocketStream` to use `RTCPeerConnection` instead of binary JPEG frames; UI components are transport-agnostic.
- WebXR scene currently streams MJPEG textures; upgrading to WebRTC will reduce latency and improve XR smoothness.

### 7. Testing & Linting
```bash
npm run lint
npm run typecheck
```
- Add React Testing Library + Vitest for component coverage as needed.

