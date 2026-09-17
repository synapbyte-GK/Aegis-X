from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Session
from datetime import datetime

from database import Base, SessionLocal


router = APIRouter()


class IncidentDB(Base):
    __tablename__ = "incidents"

    incident_id = Column(String, primary_key=True, index=True)
    event_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, nullable=False)


class Incident(BaseModel):
    incident_id: str
    event_id: str
    device_id: str
    title: str
    description: str
    severity: str
    risk_level: str
    status: str = "OPEN"
    created_at: datetime


class IncidentStatusUpdate(BaseModel):
    status: str


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/incidents")
def create_incident(
    incident: Incident,
    db: Session = Depends(get_db)
):

    new_incident = IncidentDB(
        incident_id=incident.incident_id,
        event_id=incident.event_id,
        device_id=incident.device_id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        risk_level=incident.risk_level,
        status=incident.status,
        created_at=incident.created_at
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return {
        "message": "Incident created successfully",
        "incident": {
            "incident_id": new_incident.incident_id,
            "event_id": new_incident.event_id,
            "device_id": new_incident.device_id,
            "title": new_incident.title,
            "description": new_incident.description,
            "severity": new_incident.severity,
            "risk_level": new_incident.risk_level,
            "status": new_incident.status,
            "created_at": new_incident.created_at
        }
    }


@router.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):

    incidents = db.query(IncidentDB).all()

    return {
        "incidents": [
            {
                "incident_id": incident.incident_id,
                "event_id": incident.event_id,
                "device_id": incident.device_id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "risk_level": incident.risk_level,
                "status": incident.status,
                "created_at": incident.created_at
            }
            for incident in incidents
        ],
        "count": len(incidents)
    }


@router.put("/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: str,
    status_update: IncidentStatusUpdate,
    db: Session = Depends(get_db)
):

    incident = db.query(IncidentDB).filter(
        IncidentDB.incident_id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    allowed_statuses = [
        "OPEN",
        "INVESTIGATING",
        "RESOLVED"
    ]

    new_status = status_update.status.upper()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid incident status",
                "allowed_statuses": allowed_statuses
            }
        )

    incident.status = new_status

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident status updated successfully",
        "incident_id": incident.incident_id,
        "status": incident.status
    }