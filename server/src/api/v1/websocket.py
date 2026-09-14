from typing import Annotated

from fastapi import (
    APIRouter, Query, status,
    WebSocket, WebSocketDisconnect
)

from ...services.websocket import websocket_manager
from ...core.config import settings

router = APIRouter(tags=["tunnel"])

@router.websocket("/ws/connect")
async def connect_weboskcet(
    websocket: WebSocket,
    secret_key: Annotated[str, Query(description="secret_key")]
):
    if secret_key != settings.APP_TOKEN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket_manager.connect(websocket)
    # keep-alive
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await websocket_manager.disconnect()