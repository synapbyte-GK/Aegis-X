from fastapi import APIRouter
from iot.iot_soc_pipeline import run_iot_soc_pipeline


router = APIRouter()


@router.post("/iot-soc")
def iot_soc(data: dict):
    return run_iot_soc_pipeline(data)