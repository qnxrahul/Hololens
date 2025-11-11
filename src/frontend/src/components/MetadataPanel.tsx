import InsightEventCard from "./InsightEventCard";
import type { InsightEvent } from "../types/session";
import { useSession } from "../context/SessionContext";

interface MetadataPanelProps {
  events: InsightEvent[];
}

function MetadataPanel({ events }: MetadataPanelProps) {
  const { clearEvents } = useSession();

  return (
    <div className="flex h-full flex-col rounded-2xl border border-slate-800 bg-slate-950/70">
      <header className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Insight Feed</h2>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Real-time metadata overlays
          </p>
        </div>
        <button
          type="button"
          onClick={clearEvents}
          className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-300 transition hover:border-brand"
        >
          Clear
        </button>
      </header>
      <div className="flex-1 space-y-3 overflow-y-auto p-5">
        {events.length === 0 ? (
          <p className="text-sm text-slate-500">No insight events yet.</p>
        ) : (
          events
            .slice()
            .reverse()
            .map((event, index) => <InsightEventCard key={`${event.timestamp}-${index}`} event={event} />)
        )}
      </div>
    </div>
  );
}

export default MetadataPanel;
