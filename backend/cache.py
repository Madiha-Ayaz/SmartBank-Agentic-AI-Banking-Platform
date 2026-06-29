from __future__ import annotations

import json
import logging
from typing import Any, Optional

from backend.config import settings

logger = logging.getLogger("smartbank.cache")


class CacheService:
    def __init__(self) -> None:
        self._client: Optional["Redis"] = None  # noqa: F821
        self._enabled = settings.REDIS_ENABLED

    @property
    def client(self):  # noqa: ANN202
        if self._client is not None:
            return self._client
        if not self._enabled:
            return None
        try:
            import redis

            self._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            self._client.ping()
            logger.info("Redis connected")
        except Exception:
            logger.warning("Redis unavailable — caching disabled")
            self._enabled = False
            self._client = None
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        client = self.client
        if client is None:
            return None
        try:
            data = client.get(f"smartbank:{key}")
            if data:
                return json.loads(data)
        except Exception:
            logger.exception("Cache get failed")
        return None

    async def set(
        self, key: str, value: Any, ttl: int = 300
    ) -> None:
        client = self.client
        if client is None:
            return
        try:
            client.setex(f"smartbank:{key}", ttl, json.dumps(value))
        except Exception:
            logger.exception("Cache set failed")

    async def delete(self, key: str) -> None:
        client = self.client
        if client is None:
            return
        try:
            client.delete(f"smartbank:{key}")
        except Exception:
            logger.exception("Cache delete failed")

    async def invalidate_pattern(self, pattern: str) -> None:
        client = self.client
        if client is None:
            return
        try:
            for k in client.scan_iter(f"smartbank:{pattern}"):
                client.delete(k)
        except Exception:
            logger.exception("Cache invalidation failed")


cache = CacheService()
