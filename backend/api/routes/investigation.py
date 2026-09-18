from fastapi import APIRouter
from agents.investigation_agent import investigate_event


router = APIRouter()


@router.post("/investigate")
def investigate(data: dict):
    return investigate_event(data)