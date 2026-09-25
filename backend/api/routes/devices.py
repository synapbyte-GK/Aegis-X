from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Session

from database import Base, SessionLocal


router = APIRouter()


# A device is considered active when telemetry
# was received within this time window.
HEARTBEAT_TIMEOUT_SECONDS = 15


class DeviceDB(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, default="online")


class DeviceHeartbeatDB(Base):
    __tablename__ = "device_heartbeats"

    device_id = Column(String, primary_key=True, index=True)
    last_seen = Column(DateTime, nullable=True)


class Device(BaseModel):
    device_id: str
    name: str
    device_type: str
    status: str = "online"


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def record_device_heartbeat(device_id: str):
    """
    Record the latest telemetry time for a registered device.
    """

    if not device_id:
        return

    db = SessionLocal()

    try:
        device = db.query(DeviceDB).filter(
            DeviceDB.device_id == device_id
        ).first()

        # Ignore telemetry from unknown devices.
        if not device:
            return

        now = datetime.now()

        heartbeat = db.query(
            DeviceHeartbeatDB
        ).filter(
            DeviceHeartbeatDB.device_id == device_id
        ).first()

        if heartbeat:
            heartbeat.last_seen = now
        else:
            heartbeat = DeviceHeartbeatDB(
                device_id=device_id,
                last_seen=now
            )

            db.add(heartbeat)

        device.status = "online"

        db.commit()

    finally:
        db.close()


@router.get("/devices")
def get_devices(db: Session = Depends(get_db)):

    devices = (
        db.query(DeviceDB)
        .order_by(DeviceDB.device_id.asc())
        .all()
    )

    now = datetime.now()

    result = []

    for device in devices:

        heartbeat = db.query(
            DeviceHeartbeatDB
        ).filter(
            DeviceHeartbeatDB.device_id ==
            device.device_id
        ).first()

        last_seen = (
            heartbeat.last_seen
            if heartbeat
            else None
        )

        if last_seen:
            elapsed = (
                now - last_seen
            ).total_seconds()

            current_status = (
                "online"
                if elapsed <=
                HEARTBEAT_TIMEOUT_SECONDS
                else "offline"
            )
        else:
            current_status = "offline"

        result.append({
            "device_id": device.device_id,
            "name": device.name,
            "device_type": device.device_type,
            "status": current_status,
            "last_seen": last_seen
        })

    return {
        "devices": result,
        "count": len(result)
    }


@router.post("/devices")
def add_device(
    device: Device,
    db: Session = Depends(get_db)
):

    existing_device = db.query(
        DeviceDB
    ).filter(
        DeviceDB.device_id ==
        device.device_id
    ).first()

    if existing_device:
        raise HTTPException(
            status_code=409,
            detail="Device already registered"
        )

    new_device = DeviceDB(
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        status=device.status
    )

    db.add(new_device)

    db.commit()

    db.refresh(new_device)

    return {
        "message": "Device registered successfully",
        "device": {
            "device_id":
                new_device.device_id,
            "name":
                new_device.name,
            "device_type":
                new_device.device_type,
            "status":
                new_device.status
        }
    }


@router.delete("/devices/{device_id}")
def delete_device(
    device_id: str,
    db: Session = Depends(get_db)
):

    device = db.query(
        DeviceDB
    ).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    heartbeat = db.query(
        DeviceHeartbeatDB
    ).filter(
        DeviceHeartbeatDB.device_id ==
        device_id
    ).first()

    if heartbeat:
        db.delete(heartbeat)

    db.delete(device)

    db.commit()

    return {
        "message":
            "Device deleted successfully",
        "device_id":
            device_id
    }


@router.put("/devices/{device_id}")
def update_device(
    device_id: str,
    device: Device,
    db: Session = Depends(get_db)
):

    existing_device = db.query(
        DeviceDB
    ).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not existing_device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    existing_device.name = device.name
    existing_device.device_type = (
        device.device_type
    )
    existing_device.status = device.status

    db.commit()

    db.refresh(existing_device)

    return {
        "message":
            "Device updated successfully",
        "device": {
            "device_id":
                existing_device.device_id,
            "name":
                existing_device.name,
            "device_type":
                existing_device.device_type,
            "status":
                existing_device.status
        }
    }