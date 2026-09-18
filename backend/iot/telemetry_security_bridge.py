from datetime import datetime

from iot.telemetry_processor import process_telemetry


def telemetry_to_security_event(data: dict) -> dict:
    telemetry = process_telemetry(data)

    if not telemetry["anomaly_detected"]:
        return {
            "security_event_created": False,
            "telemetry": telemetry
        }

    alerts = telemetry["alerts"]

    if telemetry.get("network_activity") == "suspicious":
        event_type = "port_scan"
        severity = "high"
    elif telemetry.get("cpu_usage") is not None and telemetry["cpu_usage"] > 90:
        event_type = "device_anomaly"
        severity = "medium"
    elif telemetry.get("temperature") is not None and telemetry["temperature"] > 70:
        event_type = "device_anomaly"
        severity = "medium"
    else:
        event_type = "device_anomaly"
        severity = "low"

    return {
        "security_event_created": True,
        "event_id": f"TEL-{telemetry['device_id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "device_id": telemetry["device_id"],
        "event_type": event_type,
        "severity": severity,
        "message": "; ".join(alerts),
        "timestamp": telemetry["timestamp"],
        "telemetry": telemetry
    }