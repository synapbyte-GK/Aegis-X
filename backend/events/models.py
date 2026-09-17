from pydantic import BaseModel
from datetime import datetime


class SecurityEvent(BaseModel):
    event_id: str
    device_id: str
    event_type: str
    severity: str
    message: str
    timestamp: datetime