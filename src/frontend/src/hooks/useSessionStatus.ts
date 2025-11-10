import { useQuery } from "@tanstack/react-query";

import { getSessionStatus } from "../api/sessions";
import type { SessionStatus } from "../types/session";

export function useSessionStatus(sessionId: string | undefined) {
  return useQuery<SessionStatus, Error>({
    queryKey: ["session-status", sessionId],
    queryFn: () => {
      if (!sessionId) {
        throw new Error("Missing sessionId");
      }
      return getSessionStatus(sessionId);
    },
    enabled: Boolean(sessionId),
    refetchInterval: 5000,
    staleTime: 3000,
  });
}
