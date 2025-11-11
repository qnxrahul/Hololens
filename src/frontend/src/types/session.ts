export interface ModelConfig {
  name: string;
  version?: string;
  parameters?: Record<string, unknown>;
}

export interface VideoWindow {
  label: string;
  relative_position?: {
    x: number;
    y: number;
  };
  relative_size?: {
    width: number;
    height: number;
  };
}

export interface SessionCreatePayload {
  project_id: string;
  source_uri: string;
  consumer_device_id?: string;
  models?: ModelConfig[];
  video_window?: VideoWindow;
  metadata?: Record<string, unknown>;
}

export interface SessionStatus {
  session_id: string;
  state: "initializing" | "running" | "stopped" | "failed";
  started_at?: string;
  updated_at: string;
  stream_endpoint?: string;
}

export interface InsightEvent {
  session_id: string;
  timestamp: string;
  model?: string;
  metadata: Record<string, unknown>;
}

export interface MediaItem {
  path: string;
  url: string;
  size: number;
  modified_at: string;
}
