from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from ...services.websocket import websocket_manager

from ...core.config import settings

router = APIRouter(tags=["Tunnel"])


@router.websocket("/ws/connect")
async def connect_websocket(
    websocket: WebSocket,
    secret_key: Annotated[str, Query(description="X-WSS-Key")]
):
    if secret_key != settings.X_WSS_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await websocket_manager.disconnect()
    finally:
        await websocket_manager.disconnect()