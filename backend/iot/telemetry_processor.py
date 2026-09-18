from datetime import datetime


def process_telemetry(data: dict) -> dict:
    device_id = data.get("device_id")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    cpu_usage = data.get("cpu_usage")
    network_activity = data.get("network_activity")

    alerts = []

    if temperature is not None and temperature > 70:
        alerts.append("High device temperature detected")

    if cpu_usage is not None and cpu_usage > 90:
        alerts.append("High CPU usage detected")

    if network_activity == "suspicious":
        alerts.append("Suspicious network activity detected")

    return {
        "device_id": device_id,
        "timestamp": data.get(
            "timestamp",
            datetime.utcnow().isoformat()
        ),
        "temperature": temperature,
        "humidity": humidity,
        "cpu_usage": cpu_usage,
        "network_activity": network_activity,
        "alerts": alerts,
        "anomaly_detected": len(alerts) > 0
    }