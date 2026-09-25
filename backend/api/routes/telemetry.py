from fastapi import APIRouter

from iot.telemetry_processor import process_telemetry
from api.routes.devices import record_device_heartbeat


router = APIRouter()


@router.post("/telemetry")
def telemetry(data: dict):

    record_device_heartbeat(
        data.get("device_id")
    )

    return process_telemetry(data)