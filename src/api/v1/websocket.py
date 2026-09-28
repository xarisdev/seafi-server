from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from ...core.config import settings

from ...services.websocket import websocket_manager

router = APIRouter(tags=["Tunnel"])

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