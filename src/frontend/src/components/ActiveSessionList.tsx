import { useMutation } from "@tanstack/react-query";
import { useEffect } from "react";
import clsx from "clsx";

import { stopSession } from "../api/sessions";
import { useSession } from "../context/SessionContext";
import { useSessionStatus } from "../hooks/useSessionStatus";

function ActiveSessionList() {
  const { sessions, activeSessionId, setActiveSession, upsertSession, removeSession } = useSession();

  const stopMutation = useMutation({
    mutationFn: stopSession,
    onSuccess: (_data, sessionId) => {
      if (sessionId) {
        upsertSession({
          session_id: sessionId,
          state: "stopped",
          updated_at: new Date().toISOString(),
        });
      }
    },
  });

  if (sessions.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-5 text-sm text-slate-400">
        No active sessions. Create one to begin streaming.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80">
      <header className="border-b border-slate-800 px-5 py-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
          Sessions
        </h3>
      </header>
      <ul className="divide-y divide-slate-800">
        {sessions.map((session) => (
          <SessionRow
            key={session.session_id}
            sessionId={session.session_id}
            isActive={session.session_id === activeSessionId}
            onSelect={() => setActiveSession(session.session_id)}
            onRemove={() => removeSession(session.session_id)}
            onStop={() => stopMutation.mutate(session.session_id)}
          />
        ))}
      </ul>
    </div>
  );
}

function SessionRow({
  sessionId,
  isActive,
  onSelect,
  onRemove,
  onStop,
}: {
  sessionId: string;
  isActive: boolean;
  onSelect: () => void;
  onRemove: () => void;
  onStop: () => void;
}) {
  const { data, isFetching } = useSessionStatus(sessionId);
  const { upsertSession } = useSession();

  useEffect(() => {
    if (data) {
      upsertSession(data);
    }
  }, [data, upsertSession]);

  return (
    <li
      className={clsx(
        "flex flex-col gap-2 px-5 py-4 text-sm transition hover:bg-slate-900",
        isActive && "bg-slate-900/90",
      )}
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold text-white">{sessionId}</span>
        <span className="text-xs uppercase tracking-wide text-slate-400">
          {isFetching ? "updating..." : data?.state}
        </span>
      </div>
      <div className="flex items-center gap-3 text-xs text-slate-400">
        <button
          type="button"
          onClick={onSelect}
          className="rounded-md border border-slate-700 px-3 py-1 text-slate-200 transition hover:border-brand"
        >
          View
        </button>
        <button
          type="button"
          onClick={onStop}
          className="rounded-md border border-rose-500/70 px-3 py-1 text-rose-300 transition hover:bg-rose-500/10"
        >
          Stop
        </button>
        <button
          type="button"
          onClick={onRemove}
          className="rounded-md border border-slate-700 px-3 py-1 text-slate-300 transition hover:border-slate-500"
        >
          Remove
        </button>
      </div>
      {data?.started_at && (
        <p className="text-xs text-slate-500">
          Started {new Date(data.started_at).toLocaleString()}
        </p>
      )}
    </li>
  );
}

export default ActiveSessionList;
