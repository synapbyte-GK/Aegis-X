from fastapi import APIRouter
from analysis.security_analyzer import analyze_security_event


router = APIRouter()


@router.post("/security-analysis")
def security_analysis(data: dict):
    return analyze_security_event(
        event_type=data.get("event_type", ""),
        severity=data.get("severity", ""),
        message=data.get("message", "")
    )