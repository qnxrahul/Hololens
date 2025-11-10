import { useWebSocketStream } from "../hooks/useWebSocketStream";

interface StreamViewerProps {
  sessionId?: string;
}

function StreamViewer({ sessionId }: StreamViewerProps) {
  const { frameSrc, connection, error } = useWebSocketStream(sessionId);

  return (
    <div className="flex h-full min-h-[320px] flex-1 flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/70 shadow-inner">
      <header className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Live Stream</h2>
          <p className="text-xs uppercase tracking-widest text-slate-500">Session {sessionId ?? "—"}</p>
        </div>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
          {connection}
        </span>
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
    </div>
  );
}

export default StreamViewer;
