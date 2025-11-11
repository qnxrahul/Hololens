## Frontend Dashboard Architecture

### 1. Objectives
- Provide a cross-platform (desktop/tablet) web dashboard to manage ViV sessions.
- Expose session lifecycle controls (create, monitor, terminate) and visualize live video plus inference metadata.
- Integrate seamlessly with the FastAPI backend and coexist with AGUI’s existing workflows.

### 2. Technology Choices
- **Framework:** React 18 + TypeScript for predictable state and component reuse.
- **Build Tool:** Vite for fast local iteration and optimized production bundles.
- **UI Library:** Tailwind CSS (lightweight styling) + Headless UI components, keeping design AGUI-friendly.
- **State/Data Layer:** TanStack Query (react-query) to manage REST interactions and cache session state.
- **Auth Integration:** OAuth2/OIDC tokens issued by Keycloak/Authlib-compatible IdP; the dashboard injects bearer tokens into REST/WebSocket calls via local storage.
- **Streaming:** 
  - Initial: Render MJPEG stream (JPEG frames over WebSocket) using `<img>` fed by a blob URL generated from incoming frames.
  - Upgrade path: Swap to WebRTC (using browser `RTCPeerConnection`) once backend signaling is ready.

### 3. Component Layout
```
App
 ├─ HeaderBar (branding, connection status)
 ├─ SessionControls
 │    ├─ SessionForm (project/source/model selection)
 │    └─ ActiveSessionList (status, stop buttons)
 ├─ MainPane
 │    ├─ StreamViewer (video canvas + overlay toggles + WebXR entry)
 │    └─ InsightSidebar
 │         ├─ MetadataFeed (scrolling list of inference events)
 │         └─ MetricsPanel (aggregated KPIs)
 └─ Footer (latency stats, build version)
```

### 4. Data Flow
1. **Session Creation**
   - `SessionForm` submits to `POST /viv/sessions` via react-query mutation.
   - Response cached in `ActiveSessionList` and sets the current session in global state (context).

2. **Status Polling**
   - `useSessionStatus` hook polls `GET /viv/sessions/{id}` with exponential backoff to track session health.

3. **Stream Consumption**
   - `StreamViewer` opens WebSocket to `/viv/streams/{id}`.
   - Binary frames converted to Blob URLs; metadata messages dispatched to `MetadataFeed`.
   - When session ends, socket closes and UI prompts to restart.

4. **Insight Feed**
   - Metadata messages appended to a bounded list (e.g., last 100 events).
   - Provide filters (per model label) and copy-to-clipboard for analysts.

### 5. Global State & Context
- `SessionContext` (React context) stores `activeSessionId`, `sessionStatus`, and `connectivity`.
- React-query caches server responses; context stores UI selections (active overlays, quality modes).

### 6. Error Handling
- Toast notifications for API errors (axios interceptors).
- Stream fallback UI when WebSocket drops (auto retry with backoff).
- Validation errors surfaced inline in `SessionForm`.

### 7. WebXR & Visualization
- WebXR overlay (Three.js + `@react-three/xr`) renders the live stream on a floating plane for immersive review within Chrome/Edge with WebXR support.
- JPEG frames from the backend update a Three.js texture each time the WebSocket delivers a new blob.
- VR button (from `@react-three/xr`) launches XR sessions; gracefully degrades when `navigator.xr` is unavailable.
- Future: replace MJPEG with WebRTC video texture to leverage GPU decoding inside XR scene.

### 8. Theming & Accessibility
- Dark theme by default to align with AGUI; Tailwind color tokens for custom branding.
- Ensure WCAG AA contrast, focus states, keyboard shortcuts for session actions.

### 9. Packaging & Deployment
- `src/frontend` houses Vite project, built to `dist/`.
- Deploy as a static bundle behind AGUI nginx or served by FastAPI via `StaticFiles`.
- CI step: `npm run build` + lint/test (`npm run test` reserved for future component tests).

### 10. Future Enhancements
- Embed AGUI authentication flow (PKCE) directly.
- Multi-session mosaic view (grid of video streams).
- Time-synced playback controls with AGUI timelines.
- Integration with AGUI notifications/webhooks for completed analyses.

