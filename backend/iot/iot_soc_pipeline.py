from iot.telemetry_security_bridge import telemetry_to_security_event
from agents.orchestrator import run_orchestrator
from ml.anomaly_detector import TelemetryAnomalyDetector


# Normal baseline telemetry for the ML model
ML_BASELINE = [
    {
        "temperature": 25,
        "humidity": 50,
        "cpu_usage": 20
    },
    {
        "temperature": 26,
        "humidity": 52,
        "cpu_usage": 22
    },
    {
        "temperature": 24,
        "humidity": 48,
        "cpu_usage": 18
    },
    {
        "temperature": 27,
        "humidity": 51,
        "cpu_usage": 25
    },
    {
        "temperature": 23,
        "humidity": 49,
        "cpu_usage": 19
    }
]


ml_detector = TelemetryAnomalyDetector()

if not ml_detector.trained:
    ml_detector.train(ML_BASELINE)


def run_iot_soc_pipeline(data: dict) -> dict:

    # 1. Process IoT telemetry
    security_event = telemetry_to_security_event(data)

    # 2. ML anomaly detection
    ml_result = ml_detector.predict(data)

    if not security_event.get("security_event_created", False):

        if not ml_result["is_anomaly"]:
            return {
                "security_event_created": False,
                "ml_anomaly": ml_result,
                "telemetry": security_event.get(
                    "telemetry",
                    {}
                )
            }

        security_event = {
            "security_event_created": True,
            "event_id": f"ML-{data.get('device_id', 'UNKNOWN')}",
            "device_id": data.get(
                "device_id",
                "UNKNOWN"
            ),
            "event_type": "ml_anomaly",
            "severity": "medium",
            "message": "Machine learning model detected anomalous telemetry",
            "timestamp": data.get("timestamp"),
            "telemetry": security_event.get(
                "telemetry",
                {}
            )
        }

    # 3. Add ML result to security event
    security_event["ml_anomaly"] = ml_result

    # 4. Send event to Multi-Agent SOC
    soc_result = run_orchestrator(
        event_type=security_event["event_type"],
        severity=security_event["severity"],
        message=security_event["message"],
        related_events=[
            {
                "device_id": security_event["device_id"],
                "is_threat": True
            }
        ]
    )

    return {
        "security_event": security_event,
        "ml_anomaly": ml_result,
        "soc_pipeline": soc_result
    }