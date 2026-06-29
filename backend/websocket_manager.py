from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import WebSocket

from backend.config import settings

logger = logging.getLogger("smartbank.ws")


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._user_connections: dict[str, set[WebSocket]] = {}

    async def connect(
        self, ws: WebSocket, room: str = "global", user_id: Optional[str] = None
    ) -> None:
        await ws.accept()
        self._connections.setdefault(room, set()).add(ws)
        if user_id:
            self._user_connections.setdefault(user_id, set()).add(ws)
        logger.info("WS connected", room=room, user_id=user_id)

    def disconnect(
        self, ws: WebSocket, room: str = "global", user_id: Optional[str] = None
    ) -> None:
        self._connections.get(room, set()).discard(ws)
        if user_id:
            self._user_connections.get(user_id, set()).discard(ws)
        logger.info("WS disconnected", room=room, user_id=user_id)

    async def broadcast(self, room: str, event: str, data: Any) -> None:
        message = json.dumps({"event": event, "data": data})
        dead: list[WebSocket] = []
        for ws in self._connections.get(room, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.get(room, set()).discard(ws)

    async def send_to_user(
        self, user_id: str, event: str, data: Any
    ) -> None:
        message = json.dumps({"event": event, "data": data})
        dead: list[WebSocket] = []
        for ws in self._user_connections.get(user_id, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._user_connections.get(user_id, set()).discard(ws)

    async def broadcast_dashboard_update(self, stats: dict[str, Any]) -> None:
        await self.broadcast("dashboard", "stats_update", stats)

    async def broadcast_case_update(self, case: dict[str, Any]) -> None:
        await self.broadcast("dashboard", "case_update", case)

    @property
    def connection_count(self) -> int:
        return sum(len(v) for v in self._connections.values())


ws_manager = WebSocketManager()
