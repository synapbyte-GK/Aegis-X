def calculate_risk(severity: str) -> str:
    severity = severity.lower()

    if severity == "critical":
        return "CRITICAL"

    if severity == "high":
        return "HIGH"

    if severity == "medium":
        return "MEDIUM"

    if severity == "low":
        return "LOW"

    return "UNKNOWN"