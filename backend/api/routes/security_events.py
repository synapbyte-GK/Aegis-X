from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import Session
from datetime import datetime

from database import Base, SessionLocal
from detection.risk_engine import calculate_risk
from detection.threat_detector import detect_threat


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

    risk_level = calculate_risk(event.severity)

    is_threat = detect_threat(
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
    db.commit()
    db.refresh(new_event)

    return {
        "message": "Security event analyzed and saved successfully",
        "event": {
            "event_id": new_event.event_id,
            "device_id": new_event.device_id,
            "event_type": new_event.event_type,
            "severity": new_event.severity,
            "risk_level": new_event.risk_level,
            "is_threat": new_event.is_threat,
            "message": new_event.message,
            "timestamp": new_event.timestamp
        }
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