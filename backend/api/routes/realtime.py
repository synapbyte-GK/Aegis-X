from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from iot.iot_soc_pipeline import run_iot_soc_pipeline


router = APIRouter()


@router.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            result = run_iot_soc_pipeline(data)

            await websocket.send_json(result)

    except WebSocketDisconnect:
        pass