import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.connection import manager
from app.generator import create_initial_state, generate_tick

BROADCAST_INTERVAL = 0.2

router = APIRouter()


@router.websocket("/live-match")
async def live_match(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    state = create_initial_state()
    try:
        while True:
            payload = generate_tick(state)
            await manager.send(websocket, payload.model_dump_json())
            if state.status == "FINISHED":
                break
            await asyncio.sleep(BROADCAST_INTERVAL)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)