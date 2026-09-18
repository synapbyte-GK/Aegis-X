from fastapi import APIRouter
from response.response_recommender import recommend_response


router = APIRouter()


@router.post("/response-recommendation")
def response_recommendation(data: dict):
    return recommend_response(
        severity=data.get("severity", ""),
        risk_level=data.get("risk_level", ""),
        is_threat=data.get("is_threat", False),
        mitre_mapping=data.get("mitre_mapping", {})
    )