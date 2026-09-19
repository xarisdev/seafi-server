import httpx
import asyncio

from websockets.asyncio.client import connect

from typing import Any

from ..models.web import ResponseSchema
from ..app.config import settings

class WebAgent:
    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        self.wss_task: asyncio.Task | None = None

    async def init_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=settings.BASE_SERVER_URL,
                timeout=10
            )

        self.wss_task = asyncio.create_task(self._wss_listener_loop())

    async def _wss_listener_loop(self):
        while True:
            try:
                wss_url = f"{settings.WSS_SERVER_URL}?secret_key={settings.APP_API_TOKEN}"

                async with connect(wss_url) as wss:

                    while True:
                        message = await wss.recv(decode=True)
                        await self._handle_wss(message)

            except Exception as exc: # reconnect
                await asyncio.sleep(5)

    async def _handle_wss(self, message):
        print(message)

    async def close_client(self):
        if self.client:
            await self.client.aclose()
            self.client = None
        if self.wss_task:
            self.wss_task.cancel()
            self.wss_task = None

    async def fetch(self, url: str, method: str = "GET", **kwargs: Any):
        """
        Принимает аргументы httpx.AsyncClient.request (json, params, headers, ...)
        """
        if not self.client:
            return

        try:
            response = await self.client.request(method=method, url=url, **kwargs)

            if "application/json" in response.headers.get("content-type", ""):
                data = response.json()
            else:
                data = response.text        

            result = ResponseSchema(
                url=url,
                status_code=response.status_code,
                data=data 
            )
        except Exception as e:
            result = ResponseSchema(url=url, error=str(e))

        return result

web_agent = WebAgent()