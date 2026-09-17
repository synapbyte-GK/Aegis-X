def analyze_threat(
    event_type: str,
    severity: str,
    risk_level: str,
    is_threat: bool,
    mitre_mapping: dict
) -> dict:

    if not is_threat:
        return {
            "threat_detected": False,
            "analysis": "No significant threat detected.",
            "priority": "LOW"
        }

    technique_id = mitre_mapping.get("technique_id")
    technique_name = mitre_mapping.get("technique_name")

    if risk_level == "CRITICAL":
        priority = "IMMEDIATE"
    elif risk_level == "HIGH":
        priority = "HIGH"
    elif risk_level == "MEDIUM":
        priority = "MEDIUM"
    else:
        priority = "LOW"

    analysis = (
        f"Suspicious {event_type} activity detected. "
        f"Severity is {severity} and calculated risk is {risk_level}. "
    )

    if technique_id:
        analysis += (
            f"Mapped to MITRE ATT&CK technique "
            f"{technique_id} ({technique_name})."
        )

    return {
        "threat_detected": True,
        "analysis": analysis,
        "priority": priority,
        "mitre_technique_id": technique_id,
        "mitre_technique_name": technique_name
    }