from fastapi import APIRouter
from analysis.soc_pipeline import run_soc_pipeline


router = APIRouter()


@router.post("/soc-pipeline")
def soc_pipeline(data: dict):
    return run_soc_pipeline(
        event_type=data.get("event_type", ""),
        severity=data.get("severity", ""),
        message=data.get("message", "")
    )