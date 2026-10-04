import logging

from asyncio import Lock
from fastapi import WebSocket

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

    async def send_json(self, telegram_id: int, payload: dict):
        async with self._lock:
            if self.connection:
                data = {
                    "telegram_id": telegram_id,
                    "payload": payload
                }
                await self.connection.send_json(data)

websocket_manager = WebSocketManager()