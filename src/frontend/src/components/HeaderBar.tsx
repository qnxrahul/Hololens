import { useEffect, useState } from "react";

import { useSession } from "../context/SessionContext";

function HeaderBar() {
  const { activeSessionId, sessions } = useSession();
  const [xrSupported, setXrSupported] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!("xr" in navigator)) {
      setXrSupported(false);
      return;
    }
    navigator.xr
      .isSessionSupported("immersive-vr")
      .then((supported) => {
        if (!cancelled) {
          setXrSupported(supported);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setXrSupported(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 py-4 backdrop-blur">
      <div>
        <h1 className="text-xl font-semibold text-white">AGUI Video-in-Video Dashboard</h1>
        <p className="text-sm text-slate-400">
          Manage ViV sessions, monitor streams, and inspect AI-driven insights.
        </p>
      </div>
      <div className="flex items-center gap-6 text-sm text-slate-300">
        <span>Sessions: {sessions.length}</span>
        <span>
          Active:{" "}
          <strong className="text-brand">
            {activeSessionId ?? "None"}
          </strong>
        </span>
        <span
          className={`rounded-full px-3 py-1 text-xs ${
            xrSupported ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-800 text-slate-400"
          }`}
        >
          WebXR {xrSupported ? "Ready" : xrSupported === null ? "Checking…" : "Unavailable"}
        </span>
      </div>
    </header>
  );
}

export default HeaderBar;
