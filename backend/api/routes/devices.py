from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from database import Base, SessionLocal


router = APIRouter()


class DeviceDB(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, default="online")


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


@router.get("/devices")
def get_devices(db: Session = Depends(get_db)):

    devices = db.query(DeviceDB).all()

    return {
        "devices": [
            {
                "device_id": device.device_id,
                "name": device.name,
                "device_type": device.device_type,
                "status": device.status
            }
            for device in devices
        ],
        "count": len(devices)
    }


@router.post("/devices")
def add_device(device: Device, db: Session = Depends(get_db)):

    existing_device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device.device_id
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
            "device_id": new_device.device_id,
            "name": new_device.name,
            "device_type": new_device.device_type,
            "status": new_device.status
        }
    }


@router.delete("/devices/{device_id}")
def delete_device(device_id: str, db: Session = Depends(get_db)):

    device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    db.delete(device)
    db.commit()

    return {
        "message": "Device deleted successfully",
        "device_id": device_id
    }


@router.put("/devices/{device_id}")
def update_device(
    device_id: str,
    device: Device,
    db: Session = Depends(get_db)
):

    existing_device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not existing_device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    existing_device.name = device.name
    existing_device.device_type = device.device_type
    existing_device.status = device.status

    db.commit()
    db.refresh(existing_device)

    return {
        "message": "Device updated successfully",
        "device": {
            "device_id": existing_device.device_id,
            "name": existing_device.name,
            "device_type": existing_device.device_type,
            "status": existing_device.status
        }
    }