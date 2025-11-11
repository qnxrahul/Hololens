from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class AGUIConnector:
    """Thin client wrapper around AGUI data analyzer APIs."""

    def __init__(self, base_url: str, *, token: Optional[str] = None, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout

    def _client(self) -> httpx.Client:
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return httpx.Client(base_url=self._base_url, headers=headers, timeout=self._timeout)

    def fetch_stream_uri(self, project_id: str, source_uri: str) -> str:
        """Resolve a stream URI from AGUI datasets."""
        if source_uri.startswith(("rtsp://", "http://", "https://")):
            return source_uri

        endpoint = f"/projects/{project_id}/assets/{source_uri}"
        with self._client() as client:
            response = client.get(endpoint)
            response.raise_for_status()
            data = response.json()
        stream_uri = data.get("stream_uri")
        if not stream_uri:
            raise ValueError(f"AGUI did not return a stream_uri for asset {source_uri}")
        logger.debug("Resolved AGUI asset %s -> %s", source_uri, stream_uri)
        return stream_uri

    def publish_insight(self, project_id: str, payload: Dict[str, Any]) -> None:
        """Send derived insights back to AGUI."""
        endpoint = f"/projects/{project_id}/insights"
        with self._client() as client:
            response = client.post(endpoint, json=payload)
            response.raise_for_status()
        logger.debug("Published insight for project %s", project_id)

