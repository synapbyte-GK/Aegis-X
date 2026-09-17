from fastapi import FastAPI

from database import Base, engine

from api.routes.health import router as health_router
from api.routes.devices import router as devices_router
from api.routes.devices import DeviceDB


app = FastAPI(title="Aegis-X")


Base.metadata.create_all(bind=engine)


app.include_router(health_router)

app.include_router(devices_router)


@app.get("/")
def root():
    return {
        "project": "Aegis-X",
        "status": "online"
    }