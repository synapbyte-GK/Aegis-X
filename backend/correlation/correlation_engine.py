from typing import List, Dict


def correlate_events(events: List[Dict]) -> Dict:
    """
    Correlate multiple security events and identify
    whether they may belong to the same suspicious activity.
    """

    if not events:
        return {
            "correlated": False,
            "event_count": 0,
            "reason": "No events available"
        }

    device_ids = {
        event.get("device_id")
        for event in events
        if event.get("device_id")
    }

    threat_events = [
        event
        for event in events
        if event.get("is_threat") is True
    ]

    if len(threat_events) >= 2 and len(device_ids) == 1:
        return {
            "correlated": True,
            "event_count": len(events),
            "threat_count": len(threat_events),
            "device_id": list(device_ids)[0],
            "reason": "Multiple threat events detected on the same device"
        }

    return {
        "correlated": False,
        "event_count": len(events),
        "threat_count": len(threat_events),
        "reason": "No strong correlation detected"
    }