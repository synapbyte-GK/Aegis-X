from fastapi import APIRouter
from agents.response_agent import run_response_agent


router = APIRouter()


@router.post("/response-agent")
def response_agent(data: dict):
    return run_response_agent(data)