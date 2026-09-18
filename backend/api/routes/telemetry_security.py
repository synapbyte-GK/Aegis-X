from fastapi import APIRouter
from iot.telemetry_security_bridge import telemetry_to_security_event


router = APIRouter()


@router.post("/telemetry-security")
def telemetry_security(data: dict):
    return telemetry_to_security_event(data)