import logging

from asyncio import Lock
from fastapi import WebSocket

from ..models.websocket import Payload

logger = logging.getLogger("websocket")

class WebSocketManager:
    def __init__(self):
        self.connection: WebSocket | None = None
        self._lock = Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.connection = websocket

    async def disconnect(self):
        async with self._lock:
            logger.info("WebSocket connection closed")
            self.connection = None

    async def send_json(self, payload: Payload):
        try:
            async with self._lock:
                if self.connection:
                    await self.connection.send_json(
                        payload.model_dump(mode='json')
                    )
        except Exception as exc:
            logger.warning(f"Error while sending json: {exc}")

websocket_manager = WebSocketManager()