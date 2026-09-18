from fastapi import APIRouter
from iot.telemetry_processor import process_telemetry


router = APIRouter()


@router.post("/telemetry")
def telemetry(data: dict):
    return process_telemetry(data)