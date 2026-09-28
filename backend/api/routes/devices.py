from datetime import datetime
import hashlib
import hmac
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Session

from database import Base, SessionLocal
from auth.routes import get_current_user


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


class DeviceCredentialDB(Base):
    """Stores a one-way hash of each device token."""

    __tablename__ = "device_credentials"

    device_id = Column(String, primary_key=True, index=True)
    token_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
class DeviceAccessDB(Base):
    """
    Maps a registered Aegis-X user to an authorized device.
    """

    __tablename__ = "device_access"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    device_id = Column(
        String,
        ForeignKey("devices.device_id"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "device_id",
            name="uq_user_device_access",
        ),
    )


class Device(BaseModel):
    device_id: str
    name: str
    device_type: str
    status: str = "online"


class DeviceRegistration(BaseModel):
    name: str
    device_type: str
class DeviceClaimRequest(BaseModel):
    device_id: str
    device_token: str

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def hash_device_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_device_token() -> str:
    return secrets.token_urlsafe(32)


def authenticate_device(
    device_id: str,
    token: str,
    db: Session,
) -> bool:
    """Validate a device token without storing the plaintext token."""

    if not device_id or not token:
        return False

    device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not device:
        return False

    credential = db.query(DeviceCredentialDB).filter(
        DeviceCredentialDB.device_id == device_id
    ).first()

    if not credential:
        return False

    supplied_hash = hash_device_token(token)

    return hmac.compare_digest(
        supplied_hash,
        credential.token_hash,
    )


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
                last_seen=now,
            )
            db.add(heartbeat)

        device.status = "online"
        db.commit()

    finally:
        db.close()

@router.post("/devices/{device_id}/rotate-token")
def rotate_device_token(
    device_id: str,
    db: Session = Depends(get_db),
):
    """Generate a new token and invalidate the previous token."""

    device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    credential = db.query(DeviceCredentialDB).filter(
        DeviceCredentialDB.device_id == device_id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=404,
            detail="Device credential not found",
        )

    new_token = generate_device_token()

    credential.token_hash = hash_device_token(new_token)
    credential.created_at = datetime.now()

    db.commit()

    return {
        "message": "Device token rotated successfully",
        "device_id": device_id,
        "device_token": new_token,
        "token_note": "Store this token securely. The previous token is now invalid.",
    }
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
            DeviceHeartbeatDB.device_id == device.device_id
        ).first()

        last_seen = heartbeat.last_seen if heartbeat else None

        if last_seen:
            elapsed = (now - last_seen).total_seconds()
            current_status = (
                "online"
                if elapsed <= HEARTBEAT_TIMEOUT_SECONDS
                else "offline"
            )
        else:
            current_status = "offline"

        result.append({
            "device_id": device.device_id,
            "name": device.name,
            "device_type": device.device_type,
            "status": current_status,
            "last_seen": last_seen,
        })

    return {
        "devices": result,
        "count": len(result),
    }
@router.get("/my-devices")
def get_my_devices(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return only devices authorized for the logged-in user.
    """

    access_rows = (
        db.query(DeviceAccessDB)
        .filter(
            DeviceAccessDB.user_id == current_user.id
        )
        .all()
    )

    result = []

    now = datetime.now()

    for access in access_rows:
        device = (
            db.query(DeviceDB)
            .filter(
                DeviceDB.device_id ==
                access.device_id
            )
            .first()
        )

        if not device:
            continue

        heartbeat = (
            db.query(DeviceHeartbeatDB)
            .filter(
                DeviceHeartbeatDB.device_id ==
                device.device_id
            )
            .first()
        )

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

        result.append(
            {
                "device_id": device.device_id,
                "name": device.name,
                "device_type": device.device_type,
                "status": current_status,
                "last_seen": last_seen,
            }
        )

    return {
        "devices": result,
        "count": len(result),
    }


@router.post("/devices/register")
def register_device(
    registration: DeviceRegistration,
    db: Session = Depends(get_db),
):
    """Create a device identity and issue its one-time device token."""

    device_id = f"DEV-{secrets.token_hex(4).upper()}"

    while db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first():
        device_id = f"DEV-{secrets.token_hex(4).upper()}"

    token = generate_device_token()

    device = DeviceDB(
        device_id=device_id,
        name=registration.name,
        device_type=registration.device_type,
        status="offline",
    )

    credential = DeviceCredentialDB(
        device_id=device_id,
        token_hash=hash_device_token(token),
    )

    db.add(device)
    db.add(credential)
    db.commit()
    db.refresh(device)

    return {
        "message": "Device registered successfully",
        "device": {
            "device_id": device.device_id,
            "name": device.name,
            "device_type": device.device_type,
            "status": "offline",
        },
        "device_token": token,
        "token_note": "Store this token securely. It is returned only during registration.",
    }


@router.post("/devices")
@router.post("/devices/claim")
def claim_device(
    request: DeviceClaimRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Authorize a device for the logged-in user
    by validating its device token.
    """

    device = (
        db.query(DeviceDB)
        .filter(
            DeviceDB.device_id ==
            request.device_id
        )
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    credential = (
        db.query(DeviceCredentialDB)
        .filter(
            DeviceCredentialDB.device_id ==
            request.device_id
        )
        .first()
    )

    if not credential:
        raise HTTPException(
            status_code=401,
            detail="Device credential not found",
        )

    supplied_hash = hash_device_token(
        request.device_token
    )

    if not hmac.compare_digest(
        supplied_hash,
        credential.token_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid device token",
        )

    existing_access = (
        db.query(DeviceAccessDB)
        .filter(
            DeviceAccessDB.user_id ==
            current_user.id,
            DeviceAccessDB.device_id ==
            request.device_id,
        )
        .first()
    )

    if existing_access:
        return {
            "message": "Device already authorized",
            "device_id": request.device_id,
        }

    access = DeviceAccessDB(
        user_id=current_user.id,
        device_id=request.device_id,
    )

    db.add(access)
    db.commit()

    return {
        "message": "Device authorized successfully",
        "device_id": request.device_id,
        "user_id": current_user.id,
    }
def add_device(
    device: Device,
    db: Session = Depends(get_db),
):

    existing_device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device.device_id
    ).first()

    if existing_device:
        raise HTTPException(
            status_code=409,
            detail="Device already registered",
        )

    new_device = DeviceDB(
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        status=device.status,
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
            "status": new_device.status,
        },
    }


@router.delete("/devices/{device_id}")
def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
):

    device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    heartbeat = db.query(DeviceHeartbeatDB).filter(
        DeviceHeartbeatDB.device_id == device_id
    ).first()

    credential = db.query(DeviceCredentialDB).filter(
        DeviceCredentialDB.device_id == device_id
    ).first()

    if heartbeat:
        db.delete(heartbeat)

    if credential:
        db.delete(credential)

    db.delete(device)
    db.commit()

    return {
        "message": "Device deleted successfully",
        "device_id": device_id,
    }


@router.put("/devices/{device_id}")
def update_device(
    device_id: str,
    device: Device,
    db: Session = Depends(get_db),
):

    existing_device = db.query(DeviceDB).filter(
        DeviceDB.device_id == device_id
    ).first()

    if not existing_device:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
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
            "status": existing_device.status,
        },
    }
