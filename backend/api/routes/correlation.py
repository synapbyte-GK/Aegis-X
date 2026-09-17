from fastapi import APIRouter
from correlation.correlation_engine import correlate_events


router = APIRouter()


@router.post("/correlate")
def correlate_security_events(events: list[dict]):
    return correlate_events(events)