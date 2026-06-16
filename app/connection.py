import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active.append(websocket)
        logger.info("Client connected. Total: %d", len(self._active))

    def disconnect(self, websocket: WebSocket) -> None:
        self._active.remove(websocket)
        logger.info("Client disconnected. Total: %d", len(self._active))

    async def send(self, websocket: WebSocket, data: str) -> None:
        await websocket.send_text(data)

    @property
    def count(self) -> int:
        return len(self._active)


manager = ConnectionManager()