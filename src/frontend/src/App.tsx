import HeaderBar from "./components/HeaderBar";
import SessionForm from "./components/SessionForm";
import ActiveSessionList from "./components/ActiveSessionList";
import StreamViewer from "./components/StreamViewer";
import MetadataPanel from "./components/MetadataPanel";
import MediaGallery from "./components/MediaGallery";
import TokenManager from "./components/TokenManager";
import { useSession } from "./context/SessionContext";

function App() {
  const { activeSessionId, events } = useSession();

  return (
    <div className="flex h-full flex-col">
      <HeaderBar />
      <main className="flex flex-1 flex-col gap-6 p-6 lg:flex-row">
        <section className="flex w-full flex-col gap-4 lg:w-80">
          <TokenManager />
          <SessionForm />
          <ActiveSessionList />
        </section>
        <section className="flex flex-1 flex-col gap-4 overflow-hidden">
          <StreamViewer sessionId={activeSessionId} />
        </section>
        <aside className="flex w-full max-w-md shrink-0 flex-col gap-4 lg:w-96">
          <MetadataPanel events={events} />
          <MediaGallery sessionId={activeSessionId} />
        </aside>
      </main>
    </div>
  );
}

export default App;
