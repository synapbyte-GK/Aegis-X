from fastapi import FastAPI

from database import Base, engine

from api.routes.health import router as health_router
from api.routes.devices import router as devices_router
from api.routes.security_events import router as security_events_router
from api.routes.incidents import router as incidents_router

from api.routes.devices import DeviceDB
from api.routes.security_events import SecurityEventDB
from api.routes.incidents import IncidentDB


app = FastAPI(title="Aegis-X")


Base.metadata.create_all(bind=engine)


app.include_router(health_router)
app.include_router(devices_router)
app.include_router(security_events_router)
app.include_router(incidents_router)


@app.get("/")
def root():
    return {
        "project": "Aegis-X",
        "status": "online"
    }