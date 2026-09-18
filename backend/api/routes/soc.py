from fastapi import APIRouter
from agents.soc_commander import soc_command


router = APIRouter()


@router.post("/soc-command")
def soc_command_api(data: dict):
    return soc_command(data)