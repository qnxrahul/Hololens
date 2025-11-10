## HoloLens Integration Guide

### 1. Prerequisites
- Unity 2022 LTS configured with Mixed Reality Feature Tool.
- MRTK 3 (Mixed Reality Toolkit for Unity) packages installed.
- MixedReality-WebRTC (preferred) or Unity WebRTC package for peer connection support.
- Access to the ViV agent endpoint (`wss://<host>:8001/viv/streams/{sessionId}`) and REST API.

### 2. Project Setup
1. Create or open an MRTK-enabled Unity project.
2. Add the `MixedRealityToolkit` prefab to the scene (if not present).
3. Import the script `src/hololens/ViVSessionController.cs` into your Unity project (e.g., `Assets/Scripts/ViVSessionController.cs`).
4. Implement the `IWebRTCClient` interface to match your signaling approach:
   - Establish signaling channel with the ViV backend (WebSocket or REST).
   - Negotiate WebRTC SDP and ICE candidates with the backend (`aiortc`).
   - Expose `SubscribeVideoAsync` to return a `RenderTexture` updated by the remote video track.

### 3. Scene Configuration
1. Create a **Slate** or **Quad** GameObject to display the video stream.
2. Attach the `ViVSessionController` component to the object.
3. Assign:
   - `Target Surface`: the `RawImage` component rendering the ViV stream.
   - `Pause Button` and `Resume Button`: MRTK Pressable Buttons or leave null if you handle input elsewhere.
4. Provide the stream endpoint (`wss://...`) and session ID (obtained from the backend).
5. During runtime, call:
   ```csharp
   vivSessionController.Initialize(wrtcClientInstance, activeSessionId);
   ```

### 4. Interaction Patterns
- **Voice Commands**: Map MRTK Speech events to `SendControlCommand("pause")` or custom payloads.
- **Gestures**: Use MRTK hand interactions to reposition or scale the video slate.
- **Dashboard HUD**: Bind metadata messages (received via DataChannel or WebSocket) to MRTK TextMeshPro elements.

### 5. Deployment Checklist
- Enable **InternetClientServer** capability in `Package.appxmanifest`.
- Add certificate or trust root for secure WebSockets if using TLS.
- Profile performance using Holographic Remoting; target 60 FPS with minimal jitter.
- Validate end-to-end latency and adjust ViV video window size to optimize throughput.

### 6. Troubleshooting
- **Black Video**: Ensure WebRTC video track is bound to the `RenderTexture`; verify backend is publishing frames.
- **High Latency**: Reduce JPEG quality/bitrate (temporary) or migrate to WebRTC hardware encoding.
- **Auth Failures**: Acquire AGUI OAuth tokens on device and inject via HTTPS headers when creating sessions.

