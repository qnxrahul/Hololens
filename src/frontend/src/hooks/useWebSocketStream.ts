import { useEffect, useRef, useState } from "react";

import type { InsightEvent } from "../types/session";
import { useSession } from "../context/SessionContext";

interface StreamState {
  frameSrc?: string;
  connection: "idle" | "connecting" | "open" | "closed" | "error";
  error?: string;
}

const DEFAULT_WS_BASE =
  (typeof window !== "undefined" && window.location.origin.replace("http", "ws")) ||
  "ws://localhost:8001";
const tokenStorageKey = import.meta.env.VITE_AUTH_TOKEN_KEY ?? "viv_auth_token";

export function useWebSocketStream(sessionId?: string): StreamState {
  const [state, setState] = useState<StreamState>({ connection: "idle" });
  const urlRef = useRef<string>();
  const wsRef = useRef<WebSocket>();
  const { pushEvent } = useSession();

  useEffect(() => {
    if (!sessionId) {
      setState({ connection: "idle" });
      return;
    }

      const wsBase = import.meta.env.VITE_STREAM_BASE_URL ?? DEFAULT_WS_BASE;
      const token = typeof window !== "undefined" ? localStorage.getItem(tokenStorageKey) : null;
      const url = new URL(`${wsBase.replace(/\/$/, "")}/viv/streams/${sessionId}`);
      if (token) {
        url.searchParams.set("token", token);
      }
      const wsUrl = url.toString();
    setState({ connection: "connecting" });

    const ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;

    ws.onopen = () => setState((prev) => ({ ...prev, connection: "open" }));

    ws.onmessage = (event) => {
        if (typeof event.data === "string") {
          try {
            const message = JSON.parse(event.data);
            if (message.type === "metadata") {
              const payload = message.payload as {
                session_id: string;
                timestamp: string;
                overlays: Array<{ model: string; metadata: Record<string, unknown> }>;
                media_url?: string;
              };
              payload?.overlays?.forEach((overlay) => {
                const insightEvent: InsightEvent = {
                  session_id: payload.session_id ?? sessionId,
                  timestamp: payload.timestamp ?? new Date().toISOString(),
                  model: overlay.model,
                  metadata: overlay.metadata,
                };
                pushEvent(insightEvent);
              });
              if (payload?.media_url) {
                pushEvent({
                  session_id: payload.session_id ?? sessionId,
                  timestamp: payload.timestamp ?? new Date().toISOString(),
                  model: "media/snapshot",
                  metadata: { url: payload.media_url },
                });
              }
            }
          } catch (err) {
            console.warn("Failed to parse metadata message", err);
          }
          return;
        }

      const blob = new Blob([event.data], { type: "image/jpeg" });
      const objectUrl = URL.createObjectURL(blob);
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
      }
      urlRef.current = objectUrl;
      setState({
        connection: "open",
        frameSrc: objectUrl,
      });
    };

    ws.onerror = () =>
      setState((prev) => ({
        ...prev,
        connection: "error",
        error: "WebSocket error occurred",
      }));

    ws.onclose = () => {
      setState((prev) => ({
        ...prev,
        connection: "closed",
      }));
    };

    return () => {
      ws.close();
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
        urlRef.current = undefined;
      }
    };
  }, [sessionId, pushEvent]);

  return state;
}
