from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import numpy as np

from ..schemas.session import ModelConfig, SessionCreate
from ..services.agui_connector import AGUIConnector
from ..services.frame_ingestor import FrameIngestSettings, FrameIngestor
from ..services.inference_orchestrator import GrayscaleDebugBackend, InferenceOrchestrator
from ..services.insight_publisher import InsightPublisher
from ..services.video_composer import VideoComposer
from ..utils.encoding import encode_jpeg


@dataclass
class SessionContext:
    """Runtime helpers and metadata for a session."""

    session_id: str
    config: SessionCreate
    publisher: InsightPublisher


class VideoInVideoAgent:
    """Coordinates ingestion, inference, picture-in-picture composition, and publishing."""

    def __init__(
        self,
        agui_connector: AGUIConnector,
        orchestrator: Optional[InferenceOrchestrator] = None,
        composer: Optional[VideoComposer] = None,
    ) -> None:
        self._agui = agui_connector
        self._orchestrator = orchestrator or InferenceOrchestrator(
            backends=[GrayscaleDebugBackend()]
        )
        self._composer = composer or VideoComposer()

    async def run_session(
        self,
        context: SessionContext,
        *,
        max_frames: Optional[int] = None,
        publish_insights: bool = True,
    ) -> None:
        """Main processing loop for a ViV session."""
        stream_uri = self._agui.fetch_stream_uri(
            context.config.project_id, context.config.source_uri
        )
        ingestor = FrameIngestor(
            FrameIngestSettings(
                source_uri=stream_uri,
                target_fps=context.config.metadata.get("target_fps")
                if context.config.metadata
                else None,
            )
        )

        model_requests = [
            {"name": model.name, "parameters": model.parameters}
            for model in self._normalize_models(context.config.models)
        ]

        frames_processed = 0
        try:
            async for frame in ingestor.frames():
                overlays = self._orchestrator.infer(frame, model_requests=model_requests)
                inset = self._select_inset_frame(frame, overlays["frames"])
                composite = self._compose_frame(frame, inset, context.config)
                payload = {
                    "session_id": context.session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "overlays": overlays["overlays"],
                }
                await context.publisher.broadcast_metadata(payload)
                encoded = encode_jpeg(composite)
                await context.publisher.broadcast_frame(encoded)

                if publish_insights:
                    asyncio.create_task(
                        self._push_insight(context, overlays["overlays"])
                    )

                frames_processed += 1
                if max_frames and frames_processed >= max_frames:
                    break
        finally:
            await ingestor.close()

    async def _push_insight(self, context: SessionContext, overlays: List[dict]) -> None:
        if not overlays:
            return
        payload = {
            "session_id": context.session_id,
            "generated_at": datetime.utcnow().isoformat(),
            "overlays": overlays,
            "metadata": context.config.metadata,
        }
        try:
            self._agui.publish_insight(context.config.project_id, payload)
        except Exception:  # pragma: no cover - network side effects ignored in scaffold
            pass

    def _normalize_models(self, models: List[ModelConfig]) -> List[ModelConfig]:
        if not models:
            return [ModelConfig(name=GrayscaleDebugBackend.name)]
        return models

    def _select_inset_frame(self, base_frame: np.ndarray, generated_frames: List[np.ndarray]) -> np.ndarray:
        if generated_frames:
            return generated_frames[0]
        return base_frame

    def _compose_frame(self, base_frame: np.ndarray, inset_frame: np.ndarray, config: SessionCreate) -> np.ndarray:
        h, w, _ = base_frame.shape
        window = config.video_window
        pos = (
            int(window.relative_position["x"] * w),
            int(window.relative_position["y"] * h),
        )
        size = (
            int(window.relative_size["width"] * w),
            int(window.relative_size["height"] * h),
        )
        return self._composer.compose(base_frame, inset_frame, position=pos, size=size)

