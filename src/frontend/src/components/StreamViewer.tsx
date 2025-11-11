import { useState } from "react";

import { useWebSocketStream } from "../hooks/useWebSocketStream";
import XRViewer from "./XRViewer";

interface StreamViewerProps {
  sessionId?: string;
}

function StreamViewer({ sessionId }: StreamViewerProps) {
  const [xrOpen, setXrOpen] = useState(false);
  const { frameSrc, connection, error } = useWebSocketStream(sessionId);

  return (
    <div className="flex h-full min-h-[320px] flex-1 flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/70 shadow-inner">
      <header className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Live Stream</h2>
          <p className="text-xs uppercase tracking-widest text-slate-500">Session {sessionId ?? "—"}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
            {connection}
          </span>
          <button
            type="button"
            disabled={!frameSrc}
            onClick={() => setXrOpen(true)}
            className="rounded-md border border-brand px-3 py-1 text-xs font-semibold text-brand transition hover:bg-brand/20 disabled:cursor-not-allowed disabled:border-slate-700 disabled:text-slate-500"
          >
            Open WebXR
          </button>
        </div>
      </header>
      <div className="relative flex flex-1 items-center justify-center bg-slate-900">
        {!sessionId && (
          <p className="text-sm text-slate-500">Select or create a session to view the stream.</p>
        )}
        {sessionId && !frameSrc && (
          <p className="text-sm text-slate-400">Waiting for frames...</p>
        )}
        {frameSrc && (
          <img
            src={frameSrc}
            className="h-full w-full object-contain"
            alt="Video-in-Video Stream"
          />
        )}
        {error && (
          <div className="absolute bottom-4 left-1/2 w-80 -translate-x-1/2 rounded-md bg-rose-500/20 px-3 py-2 text-center text-xs text-rose-200">
            {error}
          </div>
        )}
      </div>
      {xrOpen && <XRViewer frameSrc={frameSrc} onClose={() => setXrOpen(false)} />}
    </div>
  );
}

export default StreamViewer;
