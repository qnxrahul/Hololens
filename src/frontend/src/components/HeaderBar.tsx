import { useSession } from "../context/SessionContext";

function HeaderBar() {
  const { activeSessionId, sessions } = useSession();

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
      </div>
    </header>
  );
}

export default HeaderBar;
