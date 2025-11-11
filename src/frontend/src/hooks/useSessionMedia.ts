import { useQuery } from "@tanstack/react-query";

import { getSessionMedia } from "../api/sessions";
import type { MediaItem } from "../types/session";

export function useSessionMedia(sessionId: string | undefined) {
  return useQuery<MediaItem[], Error>({
    queryKey: ["session-media", sessionId],
    queryFn: () => {
      if (!sessionId) {
        throw new Error("Missing sessionId");
      }
      return getSessionMedia(sessionId);
    },
    enabled: Boolean(sessionId),
    refetchInterval: 15000,
    staleTime: 5000,
  });
}

