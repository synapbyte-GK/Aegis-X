from iot.telemetry_security_bridge import telemetry_to_security_event
from agents.orchestrator import run_orchestrator


def run_iot_soc_pipeline(data: dict) -> dict:

    security_event = telemetry_to_security_event(data)

    if not security_event.get("security_event_created", False):
        return {
            "security_event_created": False,
            "telemetry": security_event.get("telemetry", {})
        }

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
        "soc_pipeline": soc_result
    }