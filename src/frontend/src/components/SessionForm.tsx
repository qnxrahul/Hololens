import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { createSession } from "../api/sessions";
import { useSession } from "../context/SessionContext";
import type { SessionCreatePayload } from "../types/session";

const createDefaultForm = (): SessionCreatePayload => ({
  project_id: "",
  source_uri: "",
  models: [{ name: "debug/grayscale" }],
  metadata: {},
});

function SessionForm() {
  const [form, setForm] = useState<SessionCreatePayload>(() => createDefaultForm());
  const { upsertSession, setActiveSession, clearEvents } = useSession();

  const { mutateAsync, isPending, error } = useMutation({
    mutationFn: createSession,
    onSuccess: (session) => {
      upsertSession(session);
      setActiveSession(session.session_id);
      clearEvents();
      setForm(createDefaultForm());
    },
  });

  const handleChange = (field: keyof SessionCreatePayload, value: unknown) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!form.project_id || !form.source_uri) {
      return;
    }
    await mutateAsync({
      ...form,
      metadata: {
        ...form.metadata,
      },
    });
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold text-white">Start New Session</h2>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-2 text-sm">
          <span className="text-slate-300">Project ID</span>
          <input
            required
            className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-brand focus:outline-none"
            value={form.project_id}
            onChange={(event) => handleChange("project_id", event.target.value)}
            placeholder="demo-project"
          />
        </label>

        <label className="flex flex-col gap-2 text-sm">
          <span className="text-slate-300">Source URI or Asset ID</span>
          <input
            required
            className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-brand focus:outline-none"
            value={form.source_uri}
            onChange={(event) => handleChange("source_uri", event.target.value)}
            placeholder="rtsp://camera/stream"
          />
        </label>

        <label className="flex flex-col gap-2 text-sm">
          <span className="text-slate-300">Model Name</span>
          <input
            className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-brand focus:outline-none"
            value={form.models?.[0]?.name ?? ""}
            onChange={(event) =>
              handleChange("models", [{ name: event.target.value || "debug/grayscale" }])
            }
            placeholder="debug/grayscale"
          />
        </label>

        <label className="flex flex-col gap-2 text-sm">
          <span className="text-slate-300">Max Frames (optional)</span>
          <input
            type="number"
            min={0}
            className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-brand focus:outline-none"
            value={(form.metadata?.max_frames as number | undefined) ?? ""}
            onChange={(event) =>
              handleChange("metadata", {
                ...form.metadata,
                max_frames: event.target.value ? Number(event.target.value) : undefined,
              })
            }
            placeholder="e.g. 500"
          />
        </label>

        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-brand px-4 py-2 font-semibold text-white transition hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isPending ? "Starting..." : "Start Session"}
        </button>

        {error && (
          <p className="text-sm text-rose-400">
            {(error as Error).message || "Failed to start session"}
          </p>
        )}
      </form>
    </div>
  );
}

export default SessionForm;
