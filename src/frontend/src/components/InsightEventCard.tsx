import type { InsightEvent } from "../types/session";

interface InsightEventCardProps {
  event: InsightEvent;
}

function InsightEventCard({ event }: InsightEventCardProps) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3 text-xs text-slate-200 shadow-sm">
      <div className="flex items-center justify-between text-slate-400">
        <span className="font-medium text-slate-200">{event.model ?? "Unknown model"}</span>
        <time>{new Date(event.timestamp).toLocaleTimeString()}</time>
      </div>
      <pre className="mt-2 max-h-40 overflow-auto rounded bg-slate-950/60 p-2 text-[11px] text-slate-300">
        {JSON.stringify(event.metadata, null, 2)}
      </pre>
    </div>
  );
}

export default InsightEventCard;
