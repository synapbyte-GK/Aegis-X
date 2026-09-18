from fastapi import APIRouter
from agents.threat_analysis_agent import run_threat_analysis


router = APIRouter()


@router.post("/threat-analysis-agent")
def threat_analysis_agent(data: dict):
    return run_threat_analysis(data)