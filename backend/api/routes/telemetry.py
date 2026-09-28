from fastapi import APIRouter, HTTPException

from iot.telemetry_processor import process_telemetry
from api.routes.devices import (
    authenticate_device,
    record_device_heartbeat,
)
from database import SessionLocal


router = APIRouter()


@router.post("/telemetry")
def telemetry(data: dict):

    device_id = data.get("device_id")
    device_token = data.get("device_token")

    if not device_id:
        raise HTTPException(
            status_code=400,
            detail="device_id is required",
        )

    if not device_token:
        raise HTTPException(
            status_code=401,
            detail="device_token is required",
        )

    db = SessionLocal()

    try:
        authenticated = authenticate_device(
            device_id=device_id,
            token=device_token,
            db=db,
        )
    finally:
        db.close()

    if not authenticated:
        raise HTTPException(
            status_code=401,
            detail="Invalid device credentials",
        )

    record_device_heartbeat(device_id)

    return process_telemetry(data)