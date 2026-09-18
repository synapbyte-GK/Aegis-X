def recommend_response(
    severity: str,
    risk_level: str,
    is_threat: bool,
    mitre_mapping: dict
) -> dict:

    if not is_threat:
        return {
            "action_required": False,
            "recommended_action": "Continue monitoring",
            "approval_required": False
        }

    technique_id = mitre_mapping.get("technique_id")

    if risk_level == "CRITICAL":
        action = "Isolate affected device in the controlled lab and start incident investigation"
    elif risk_level == "HIGH":
        action = "Temporarily restrict the affected device and investigate the security event"
    elif risk_level == "MEDIUM":
        action = "Increase monitoring and review related security events"
    else:
        action = "Continue monitoring the affected device"

    return {
        "action_required": True,
        "recommended_action": action,
        "mitre_technique_id": technique_id,
        "approval_required": True
    }