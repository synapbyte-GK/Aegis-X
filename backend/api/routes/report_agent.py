from fastapi import APIRouter
from agents.report_agent import generate_report


router = APIRouter()


@router.post("/report-agent")
def report_agent(data: dict):
    return generate_report(
        security_analysis=data.get(
            "security_analysis",
            {}
        ),
        investigation=data.get(
            "investigation",
            {}
        ),
        soc_decision=data.get(
            "soc_decision",
            {}
        )
    )