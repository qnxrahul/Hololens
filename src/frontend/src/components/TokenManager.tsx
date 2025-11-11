import { useState, useEffect } from "react";

import { useAuth } from "../context/AuthContext";

function TokenManager() {
  const { token, setToken, clearToken } = useAuth();
  const [draft, setDraft] = useState("");

  useEffect(() => {
    setDraft(token ?? "");
  }, [token]);

  const handleSave = () => {
    const trimmed = draft.trim();
    if (trimmed.length === 0) {
      clearToken();
    } else {
      setToken(trimmed);
    }
  };

  const hasToken = Boolean(token && token.length > 0);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-200 shadow">
      <header className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-white">Auth Token</h2>
          <p className="text-xs text-slate-400">Paste an OAuth access token to authorize requests.</p>
        </div>
        <span className={`rounded-full px-2 py-1 text-[11px] uppercase tracking-wide ${hasToken ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-800 text-slate-400"}`}>
          {hasToken ? "Configured" : "Missing"}
        </span>
      </header>
      <textarea
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        rows={3}
        placeholder="Paste bearer token..."
        className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100 focus:border-brand focus:outline-none"
      />
      <div className="mt-3 flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          className="rounded-md bg-brand px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-brand-dark"
        >
          Save Token
        </button>
        <button
          type="button"
          onClick={() => {
            clearToken();
            setDraft("");
          }}
          className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 transition hover:border-rose-500 hover:text-rose-300"
        >
          Clear
        </button>
      </div>
    </div>
  );
}

export default TokenManager;
