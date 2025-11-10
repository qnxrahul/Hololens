import type { SessionCreatePayload, SessionStatus } from "../types/session";
import { apiClient } from "./client";

export async function createSession(payload: SessionCreatePayload): Promise<SessionStatus> {
  const { data } = await apiClient.post<SessionStatus>("/viv/sessions", payload);
  return data;
}

export async function getSessionStatus(sessionId: string): Promise<SessionStatus> {
  const { data } = await apiClient.get<SessionStatus>(`/viv/sessions/${sessionId}`);
  return data;
}

export async function stopSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/viv/sessions/${sessionId}`);
}
