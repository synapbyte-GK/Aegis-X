from fastapi import APIRouter
from detection.threat_analyzer import analyze_threat


router = APIRouter()


@router.post("/threat-analysis")
def threat_analysis(data: dict):
    return analyze_threat(
        event_type=data.get("event_type", ""),
        severity=data.get("severity", ""),
        risk_level=data.get("risk_level", ""),
        is_threat=data.get("is_threat", False),
        mitre_mapping=data.get("mitre_mapping", {})
    )