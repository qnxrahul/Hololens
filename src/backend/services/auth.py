from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from jose import JWTError, jwt

logger = logging.getLogger(__name__)


@dataclass
class JWKSSettings:
    jwks_url: str
    audience: Optional[str] = None
    issuer: Optional[str] = None
    refresh_seconds: int = 300


class JWKSAuthenticator:
    """Fetches JWKS and validates JSON Web Tokens from identity providers like Keycloak."""

    def __init__(self, settings: JWKSSettings) -> None:
        self._settings = settings
        self._jwks: Optional[Dict[str, Any]] = None
        self._last_refresh: float = 0.0
        self._lock = asyncio.Lock()

    async def _ensure_jwks(self) -> Dict[str, Any]:
        import time

        async with self._lock:
            now = time.time()
            if self._jwks and now - self._last_refresh < self._settings.refresh_seconds:
                return self._jwks
            async with httpx.AsyncClient() as client:
                response = await client.get(self._settings.jwks_url, timeout=10.0)
                response.raise_for_status()
                self._jwks = response.json()
                self._last_refresh = now
                logger.info("Refreshed JWKS keys from %s", self._settings.jwks_url)
            return self._jwks

    async def verify_token(self, token: str) -> Dict[str, Any]:
        jwks = await self._ensure_jwks()
        try:
            unverified_header = jwt.get_unverified_header(token)
        except JWTError as exc:  # pragma: no cover - malformed token
            raise PermissionError("Invalid token header") from exc

        key = next(
            (k for k in jwks.get("keys", []) if k.get("kid") == unverified_header.get("kid")),
            None,
        )
        if key is None:
            await self._refresh_keys_and_raise()

        options = {"verify_aud": self._settings.audience is not None}
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=[unverified_header.get("alg", "RS256")],
                audience=self._settings.audience,
                issuer=self._settings.issuer,
                options=options,
            )
            return payload
        except JWTError as exc:
            logger.warning("Token verification failed: %s", exc)
            raise PermissionError("Token verification failed") from exc

    async def _refresh_keys_and_raise(self) -> None:
        async with self._lock:
            self._jwks = None
        await self._ensure_jwks()
        raise PermissionError("Unable to locate matching key for token")

