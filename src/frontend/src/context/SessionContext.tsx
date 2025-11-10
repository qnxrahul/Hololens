import { createContext, useCallback, useContext, useMemo, useReducer } from "react";

import type { InsightEvent, SessionStatus } from "../types/session";

interface SessionState {
  sessions: SessionStatus[];
  activeSessionId?: string;
  events: InsightEvent[];
}

type Action =
  | { type: "UPSERT_SESSION"; payload: SessionStatus }
  | { type: "REMOVE_SESSION"; payload: { sessionId: string } }
  | { type: "SET_ACTIVE_SESSION"; payload?: { sessionId?: string } }
  | { type: "PUSH_EVENT"; payload: InsightEvent }
  | { type: "CLEAR_EVENTS" };

const initialState: SessionState = {
  sessions: [],
  activeSessionId: undefined,
  events: [],
};

function reducer(state: SessionState, action: Action): SessionState {
  switch (action.type) {
    case "UPSERT_SESSION": {
      const existingIndex = state.sessions.findIndex(
        (session) => session.session_id === action.payload.session_id,
      );
      if (existingIndex >= 0) {
        const nextSessions = [...state.sessions];
        nextSessions[existingIndex] = { ...nextSessions[existingIndex], ...action.payload };
        return { ...state, sessions: nextSessions };
      }
      return { ...state, sessions: [action.payload, ...state.sessions] };
    }
    case "REMOVE_SESSION": {
      const filtered = state.sessions.filter((session) => session.session_id !== action.payload.sessionId);
      const isActive = state.activeSessionId === action.payload.sessionId;
      return {
        ...state,
        sessions: filtered,
        activeSessionId: isActive ? filtered[0]?.session_id : state.activeSessionId,
      };
    }
    case "SET_ACTIVE_SESSION":
      return {
        ...state,
        activeSessionId: action.payload?.sessionId,
        events: state.events.filter((event) => event.session_id === action.payload?.sessionId),
      };
    case "PUSH_EVENT": {
      const events = [...state.events, action.payload].slice(-100);
      return { ...state, events };
    }
    case "CLEAR_EVENTS":
      return { ...state, events: [] };
    default:
      return state;
  }
}

interface SessionContextValue extends SessionState {
  upsertSession: (status: SessionStatus) => void;
  removeSession: (sessionId: string) => void;
  setActiveSession: (sessionId?: string) => void;
  pushEvent: (event: InsightEvent) => void;
  clearEvents: () => void;
}

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const upsertSession = useCallback(
    (status: SessionStatus) => dispatch({ type: "UPSERT_SESSION", payload: status }),
    [],
  );
  const removeSession = useCallback(
    (sessionId: string) => dispatch({ type: "REMOVE_SESSION", payload: { sessionId } }),
    [],
  );
  const setActiveSession = useCallback(
    (sessionId?: string) => dispatch({ type: "SET_ACTIVE_SESSION", payload: { sessionId } }),
    [],
  );
  const pushEvent = useCallback(
    (event: InsightEvent) => dispatch({ type: "PUSH_EVENT", payload: event }),
    [],
  );
  const clearEvents = useCallback(() => dispatch({ type: "CLEAR_EVENTS" }), []);

  const value = useMemo(
    () => ({
      sessions: state.sessions,
      activeSessionId: state.activeSessionId,
      events: state.events,
      upsertSession,
      removeSession,
      setActiveSession,
      pushEvent,
      clearEvents,
    }),
    [
      state.sessions,
      state.activeSessionId,
      state.events,
      upsertSession,
      removeSession,
      setActiveSession,
      pushEvent,
      clearEvents,
    ],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionContextValue {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
