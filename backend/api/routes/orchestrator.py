from fastapi import APIRouter
from agents.orchestrator import run_orchestrator


router = APIRouter()


@router.post("/orchestrator")
def orchestrator(data: dict):
    return run_orchestrator(
        event_type=data.get("event_type", ""),
        severity=data.get("severity", ""),
        message=data.get("message", ""),
        related_events=data.get("related_events")
    )