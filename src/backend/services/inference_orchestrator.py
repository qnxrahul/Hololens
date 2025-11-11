from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Protocol

import numpy as np


class InferenceBackend(Protocol):
    """Interface for inference engines used by the orchestrator."""

    name: str

    def infer(self, frame: np.ndarray, *, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...


class GrayscaleDebugBackend:
    """Trivial backend that converts the frame to grayscale as a placeholder output."""

    name = "debug/grayscale"

    def infer(self, frame: np.ndarray, *, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        gray = frame.mean(axis=2, keepdims=True)
        return {
            "frame": np.repeat(gray, 3, axis=2),
            "metadata": {
                "description": "Grayscale conversion placeholder",
            },
        }


class InferenceOrchestrator:
    """Dispatches frames to one or more inference backends and aggregates their results."""

    def __init__(self, backends: Optional[Iterable[InferenceBackend]] = None) -> None:
        self._backends: Dict[str, InferenceBackend] = {}
        if backends:
            for backend in backends:
                self.register_backend(backend)

    def register_backend(self, backend: InferenceBackend) -> None:
        if backend.name in self._backends:
            raise ValueError(f"Backend '{backend.name}' already registered.")
        self._backends[backend.name] = backend

    def infer(
        self,
        frame: np.ndarray,
        *,
        model_requests: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Run inference with the requested models and return merged metadata."""
        results: Dict[str, Any] = {"overlays": [], "frames": []}
        model_requests = model_requests or [{"name": GrayscaleDebugBackend.name, "parameters": None}]

        for request in model_requests:
            name = request.get("name")
            parameters = request.get("parameters")
            backend = self._backends.get(name)
            if backend is None:
                raise KeyError(f"Unknown inference backend '{name}'.")
            outcome = backend.infer(frame, parameters=parameters)
            if "frame" in outcome:
                results["frames"].append(outcome["frame"])
            if "metadata" in outcome:
                results["overlays"].append({"model": name, "metadata": outcome["metadata"]})
        return results

