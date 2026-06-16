import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    def add(self, live_id: str, websocket: WebSocket):
        self._connections.setdefault(live_id, []).append(websocket)
        logger.info("[ws_manager] add live_id=%s total=%d", live_id, len(self._connections[live_id]))

    def remove(self, live_id: str, websocket: WebSocket):
        conns = self._connections.get(live_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._connections.pop(live_id, None)
        logger.info("[ws_manager] remove live_id=%s remaining=%d", live_id, len(self._connections.get(live_id, [])))

    async def broadcast(self, live_id: str, message: dict):
        conns = list(self._connections.get(live_id, []))
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.remove(live_id, ws)


manager = ConnectionManager()
