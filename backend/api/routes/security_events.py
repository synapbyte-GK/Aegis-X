from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import Session
from datetime import datetime

from database import Base, SessionLocal
from detection.risk_engine import calculate_risk
from detection.threat_detector import detect_threat
from mitre.attack_mapper import map_to_attack
from api.routes.incidents import IncidentDB


router = APIRouter()


class SecurityEventDB(Base):
    __tablename__ = "security_events"

    event_id = Column(String, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    is_threat = Column(Boolean, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


class SecurityEvent(BaseModel):
    event_id: str
    device_id: str
    event_type: str
    severity: str
    message: str
    timestamp: datetime


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/security-events")
def create_security_event(
    event: SecurityEvent,
    db: Session = Depends(get_db)
):

    existing_event = db.query(SecurityEventDB).filter(
        SecurityEventDB.event_id == event.event_id
    ).first()

    if existing_event:
        raise HTTPException(
            status_code=409,
            detail="Security event already exists"
        )

    risk_level = calculate_risk(event.severity)

    is_threat = detect_threat(
        event.event_type,
        event.message
    )

    mitre_mapping = map_to_attack(
        event.event_type,
        event.message
    )

    new_event = SecurityEventDB(
        event_id=event.event_id,
        device_id=event.device_id,
        event_type=event.event_type,
        severity=event.severity,
        risk_level=risk_level,
        is_threat=is_threat,
        message=event.message,
        timestamp=event.timestamp
    )

    db.add(new_event)

    created_incident = None

    if is_threat:

        existing_incident = db.query(IncidentDB).filter(
            IncidentDB.event_id == event.event_id
        ).first()

        if not existing_incident:

            technique_id = mitre_mapping.get("technique_id")
            technique_name = mitre_mapping.get("technique_name")

            incident_title = "Automatic Threat Detection"

            if technique_id:
                incident_title = (
                    f"Automatic Threat Detection - "
                    f"{technique_id}: {technique_name}"
                )

            created_incident = IncidentDB(
                incident_id=f"INC-{event.event_id}",
                event_id=event.event_id,
                device_id=event.device_id,
                title=incident_title,
                description=event.message,
                severity=event.severity,
                risk_level=risk_level,
                status="OPEN",
                created_at=event.timestamp
            )

            db.add(created_incident)

    db.commit()
    db.refresh(new_event)

    return {
        "message": "Security event analyzed successfully",
        "event": {
            "event_id": new_event.event_id,
            "device_id": new_event.device_id,
            "event_type": new_event.event_type,
            "severity": new_event.severity,
            "risk_level": new_event.risk_level,
            "is_threat": new_event.is_threat,
            "message": new_event.message,
            "timestamp": new_event.timestamp
        },
        "mitre_mapping": mitre_mapping,
        "incident_created": created_incident is not None
    }


@router.get("/security-events")
def get_security_events(db: Session = Depends(get_db)):

    events = db.query(SecurityEventDB).all()

    return {
        "events": [
            {
                "event_id": event.event_id,
                "device_id": event.device_id,
                "event_type": event.event_type,
                "severity": event.severity,
                "risk_level": event.risk_level,
                "is_threat": event.is_threat,
                "message": event.message,
                "timestamp": event.timestamp
            }
            for event in events
        ],
        "count": len(events)
    }