import asyncio
import logging

import json

from asyncio import Lock
from fastapi import WebSocket

from ..models.websocket import Payload

logger = logging.getLogger("websocket")

class WebSocketManager:
    def __init__(self):
        self.connection: WebSocket | None = None
        self.queue: asyncio.Queue = asyncio.Queue()

        self._lock = Lock()
        self._connection_event = asyncio.Event()
        self._sender_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        async with self._lock:
            self.connection = websocket
            self._connection_event.set()

        if self._sender_task is None or self._sender_task.done():
            self._sender_task = asyncio.create_task(self._sender())

    async def disconnect(self):
        async with self._lock:
            self.connection = None
            self._connection_event.clear()

        logger.info("WebSocket connection closed")

    async def _put_payload(self, payload: Payload):
        _json = payload.model_dump(mode='json')
        await self.queue.put(_json)

    async def _sender(self):
        while True:
            item = await self.queue.get()
            
            try:
                while True:
                    await self._connection_event.wait()

                    async with self._lock:
                        connection = self.connection

                    if connection is None:
                        continue

                    try:
                        await connection.send_json(item)
                        break

                    except Exception:
                        logger.exception("WebSocket send failed")

                        async with self._lock:
                            if self.connection is connection:
                                self.connection = None
                                self._connection_event.clear()

            except asyncio.CancelledError:
                raise

            finally:
                self.queue.task_done()

websocket_manager = WebSocketManager()