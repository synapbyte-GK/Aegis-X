from fastapi import APIRouter
from agents.correlation_agent import run_correlation


router = APIRouter()


@router.post("/correlation-agent")
def correlation_agent(data: list[dict]):
    return run_correlation(data)