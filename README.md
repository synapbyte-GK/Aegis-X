# Aegis-X

**Aegis-X** is a real-time AI-assisted Security Operations Center (SOC) dashboard for IoT environments. It combines IoT telemetry, device heartbeat monitoring, anomaly detection, security-event generation, MITRE ATT&CK mapping, incident tracking, and a live SOC interface in one project.

> BTech project / academic demonstration build

## What Aegis-X Does

Aegis-X continuously receives telemetry from IoT devices and evaluates it using a hybrid detection pipeline. Normal telemetry is monitored in real time, while suspicious conditions can generate security events and incidents for investigation.

### Core capabilities

- Real-time IoT telemetry over WebSocket
- Device registration and multi-device monitoring
- Device heartbeat with online/offline detection
- Last-seen timestamp tracking
- Hybrid ML + rule-based anomaly detection
- Security event generation from suspicious telemetry/activity
- MITRE ATT&CK technique mapping (including **T1046 – Network Service Scanning** for port-scan activity)
- Threat timeline and live security-event feed
- Incident history with status updates
- Investigation view for security events
- Dockerized backend and frontend
- IoT telemetry simulator for repeatable demonstrations

## Architecture

```text
                    +-----------------------+
                    |    IoT Simulator      |
                    |  ESP32-001 telemetry  |
                    +-----------+-----------+
                                |
                                | WebSocket
                                v
                    +-----------------------+
                    |     FastAPI Backend    |
                    |  Telemetry + Devices   |
                    +-----------+-----------+
                                |
              +-----------------+------------------+
              |                                    |
              v                                    v
   +-----------------------+             +-----------------------+
   | Heartbeat / Device DB |             |  IoT SOC Pipeline     |
   | Online / Offline      |             | ML + Rules Detection  |
   +-----------------------+             +-----------+-----------+
                                                    |
                                                    v
                                         +-----------------------+
                                         | Security Events       |
                                         | MITRE Mapping         |
                                         | Incident Creation     |
                                         +-----------+-----------+
                                                     |
                                                     | REST / WebSocket
                                                     v
                                         +-----------------------+
                                         | React + Vite Dashboard|
                                         | SOC Command Center    |
                                         +-----------------------+
```

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, CSS |
| Backend | Python, FastAPI, Uvicorn |
| ML | scikit-learn Isolation Forest + rules |
| Database | SQLite + SQLAlchemy |
| Realtime | WebSocket |
| IoT Demo | Python telemetry simulator |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

## Project Structure

```text
Aegis-X/
├── backend/
│   ├── agents/
│   ├── api/
│   │   └── routes/
│   ├── correlation/
│   ├── database/
│   ├── detection/
│   ├── iot/
│   ├── mitre/
│   ├── ml/
│   ├── response/
│   ├── aegis_x.db
│   ├── database.py
│   └── main.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── frontend.Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── index.css
├── iot/
├── ml/
└── simulator/
    └── iot_simulator.py
```

## Detection Logic

Aegis-X uses a hybrid approach:

1. **ML anomaly detection** evaluates telemetry against a learned normal baseline.
2. **Security rules** apply explicit thresholds and suspicious-network conditions.
3. The pipeline combines those signals before treating telemetry as a security anomaly.
4. A detected threat can create a security event and an incident record.

### Example anomaly conditions used in the current build

- Temperature at or above **60°C**
- CPU usage at or above **80%**
- Humidity below **20%** or above **80%**
- Suspicious / malicious / attack network state

The current ML baseline is trained from normal IoT telemetry samples.

## Docker Setup

From the project root:

```powershell
cd E:\Aegis-X
docker compose -f docker\docker-compose.yml up -d --build
docker compose -f docker\docker-compose.yml ps
```

Expected services:

```text
Backend   http://127.0.0.1:8002
Frontend  http://127.0.0.1:5173
```

The backend should report **healthy** in Docker Compose.

## Run the IoT Simulator

Open another terminal:

```powershell
cd E:\Aegis-X
python simulator\iot_simulator.py
```

The simulator sends telemetry for `ESP32-001` to the backend.

Normal readings use ordinary environment/CPU values. Periodic simulated anomaly readings are used to demonstrate threat detection, event generation, and incident handling.

## Dashboard Pages

### Overview

The SOC Command Center provides:

- SOC status
- Threat-alert count
- Current ML anomaly state
- Active device
- Live telemetry
- Temperature and CPU trends
- Current SOC verdict
- Security analytics
- Threat timeline
- Recent security events

### Live Events

Displays security events received from the backend, including severity, device, event type, message, and MITRE information when available.

### Devices

Shows all registered devices with:

- Online / offline state
- Last seen time
- Device type
- Current telemetry for the active device
- Live telemetry indicator

Heartbeat timeout in the current backend build is **15 seconds**.

### Investigation

Provides a focused view for examining a selected security event and its associated threat information.

### Incident History

Shows incident records and allows incident-status updates through the dashboard.

### MITRE ATT&CK

Displays technique mappings associated with detected activity. A current demonstrated example is:

**T1046 — Network Service Scanning**

## Demonstration Flow

Use this sequence for a project demo:

```text
1. Start Docker services
2. Start the IoT simulator
3. Open the Aegis-X dashboard
4. Show ESP32-001 live telemetry
5. Show device heartbeat and Last Seen
6. Demonstrate normal telemetry
7. Trigger / wait for a simulated threat
8. Show the generated HIGH severity event
9. Show MITRE T1046 mapping for port-scan activity
10. Open Investigation
11. Open Incident History
12. Stop the simulator and demonstrate OFFLINE state after timeout
```

## Current Demonstrated IoT Device

```text
Device ID   : ESP32-001
Name        : ESP32 Weather Sensor
Type        : ESP32
```

Additional registered devices in the current build include:

```text
ESP32-002      ESP32 Environment Node
IOT-GATE-001   IoT Gateway
```

## API Endpoints Used by the Dashboard

```text
GET  /devices
POST /telemetry
GET  /security-events
GET  /incidents
PUT  /incidents/{incident_id}/status
```

The backend also exposes a WebSocket telemetry channel used by the simulator and frontend:

```text
ws://127.0.0.1:8002/ws/telemetry
```

## Development Notes

For frontend development:

```powershell
cd E:\Aegis-X\frontend
npm run build
```

The production frontend is built and served through the Docker frontend container.

## Project Status

The current build has been tested for:

- Docker backend health
- Docker frontend startup
- WebSocket telemetry flow
- ML anomaly detection
- Security-event generation
- Device heartbeat and Last Seen
- Online/offline device status
- Threat timeline
- MITRE mapping
- Incident history
- React production build
- GitHub synchronization

## GitHub

Repository: `https://github.com/synapbyte-GK/Aegis-X`

## License

This repository is intended as an academic/project demonstration unless a separate license is added by the project owner.
