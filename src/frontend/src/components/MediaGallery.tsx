import { useMemo } from "react";

import { useSessionMedia } from "../hooks/useSessionMedia";

interface MediaGalleryProps {
  sessionId?: string;
}

function formatBytes(size: number): string {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function MediaGallery({ sessionId }: MediaGalleryProps) {
  const { data, isLoading, isFetching, error, refetch } = useSessionMedia(sessionId);

  const items = useMemo(() => data ?? [], [data]);

  return (
    <div className="flex h-full flex-col rounded-2xl border border-slate-800 bg-slate-950/70">
      <header className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Saved Media</h2>
          <p className="text-xs uppercase tracking-widest text-slate-500">Snapshots &amp; exports</p>
        </div>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={!sessionId || isFetching}
          className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-300 transition hover:border-brand disabled:cursor-not-allowed disabled:opacity-60"
        >
          Refresh
        </button>
      </header>
      <div className="flex-1 space-y-3 overflow-y-auto p-5 text-sm">
        {!sessionId && <p className="text-slate-500">Select a session to view captured media.</p>}
        {sessionId && isLoading && <p className="text-slate-400">Loading media...</p>}
        {error && <p className="text-rose-400">Failed to load media: {error.message}</p>}
        {sessionId && !isLoading && items.length === 0 && (
          <p className="text-slate-500">No media captured yet for this session.</p>
        )}
        {items.map((item) => (
          <div
            key={item.path}
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/80 px-4 py-2 text-xs text-slate-200"
          >
            <div className="flex flex-col">
              <span className="font-semibold text-slate-100">{item.path.split("/").pop()}</span>
              <span className="text-[11px] text-slate-500">
                {formatBytes(item.size)} · {new Date(item.modified_at).toLocaleString()}
              </span>
            </div>
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="rounded-md border border-brand px-3 py-1 text-[11px] font-semibold text-brand transition hover:bg-brand/20"
            >
              Download
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MediaGallery;
