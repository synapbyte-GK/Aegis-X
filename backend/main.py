from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from api.routes.health import router as health_router
from api.routes.devices import (
    router as devices_router,
    record_device_heartbeat,
)
from api.routes.security_events import router as security_events_router
from api.routes.incidents import router as incidents_router
from api.routes.correlation import router as correlation_router
from api.routes.mitre import router as mitre_router
from api.routes.threat_analysis import router as threat_analysis_router
from api.routes.response import router as response_router
from api.routes.security_analysis import router as security_analysis_router
from api.routes.soc import router as soc_router
from api.routes.soc_pipeline import router as soc_pipeline_router
from api.routes.investigation import router as investigation_router
from api.routes.threat_analysis_agent import (
    router as threat_analysis_agent_router
)
from api.routes.correlation_agent import (
    router as correlation_agent_router
)
from api.routes.response_agent import (
    router as response_agent_router
)
from api.routes.report_agent import (
    router as report_agent_router
)
from api.routes.orchestrator import (
    router as orchestrator_router
)
from api.routes.telemetry import router as telemetry_router
from api.routes.telemetry_security import (
    router as telemetry_security_router
)
from api.routes.iot_soc import router as iot_soc_router
from api.routes.ml_anomaly import router as ml_anomaly_router

from iot.iot_soc_pipeline import run_iot_soc_pipeline


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = FastAPI(title="Aegis-X")


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# API ROUTERS
# --------------------------------------------------

app.include_router(health_router)
app.include_router(devices_router)
app.include_router(security_events_router)
app.include_router(incidents_router)
app.include_router(correlation_router)
app.include_router(mitre_router)
app.include_router(threat_analysis_router)
app.include_router(response_router)
app.include_router(security_analysis_router)
app.include_router(soc_router)
app.include_router(soc_pipeline_router)
app.include_router(investigation_router)
app.include_router(threat_analysis_agent_router)
app.include_router(correlation_agent_router)
app.include_router(response_agent_router)
app.include_router(report_agent_router)
app.include_router(orchestrator_router)
app.include_router(telemetry_router)
app.include_router(telemetry_security_router)
app.include_router(iot_soc_router)
app.include_router(ml_anomaly_router)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "project": "Aegis-X",
        "status": "online"
    }


# --------------------------------------------------
# REAL-TIME WEBSOCKET CONNECTION MANAGER
# --------------------------------------------------

class ConnectionManager:

    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, data: dict):
        disconnected = []

        for websocket in list(self.active_connections):
            try:
                await websocket.send_json(data)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)


manager = ConnectionManager()


# --------------------------------------------------
# TELEMETRY WEBSOCKET
# --------------------------------------------------

@app.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):

    await manager.connect(websocket)

    try:

        while True:

            telemetry = await websocket.receive_json()
            record_device_heartbeat(
    telemetry.get("device_id")
)
            result = run_iot_soc_pipeline(telemetry)

            # Send SOC result to every connected client
            await manager.broadcast(result)

    except WebSocketDisconnect:

        manager.disconnect(websocket)

    except Exception:

        manager.disconnect(websocket)