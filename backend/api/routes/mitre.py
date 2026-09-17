from fastapi import APIRouter
from mitre.attack_mapper import map_to_attack


router = APIRouter()


@router.post("/mitre-map")
def mitre_mapping(event_type: str, message: str):
    return map_to_attack(event_type, message)