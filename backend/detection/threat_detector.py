def detect_threat(event_type: str, message: str) -> bool:
    event_type = event_type.lower()
    message = message.lower()

    suspicious_types = [
        "suspicious_activity",
        "unauthorized_access",
        "malware",
        "brute_force",
        "port_scan"
    ]

    suspicious_keywords = [
        "unusual",
        "suspicious",
        "unauthorized",
        "malware",
        "attack",
        "scan",
        "brute force"
    ]

    if event_type in suspicious_types:
        return True

    for keyword in suspicious_keywords:
        if keyword in message:
            return True

    return False