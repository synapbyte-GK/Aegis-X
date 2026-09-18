def soc_command(
    security_analysis: dict
) -> dict:

    risk_level = security_analysis.get("risk_level", "UNKNOWN")
    is_threat = security_analysis.get("is_threat", False)

    mitre_mapping = security_analysis.get(
        "mitre_mapping",
        {}
    )

    threat_analysis = security_analysis.get(
        "threat_analysis",
        {}
    )

    response = security_analysis.get(
        "response_recommendation",
        {}
    )

    if not is_threat:
        decision = "MONITOR"
        priority = "LOW"
    elif risk_level == "CRITICAL":
        decision = "IMMEDIATE_REVIEW"
        priority = "CRITICAL"
    elif risk_level == "HIGH":
        decision = "INVESTIGATE"
        priority = "HIGH"
    elif risk_level == "MEDIUM":
        decision = "MONITOR_CLOSELY"
        priority = "MEDIUM"
    else:
        decision = "MONITOR"
        priority = "LOW"

    return {
        "decision": decision,
        "priority": priority,
        "risk_level": risk_level,
        "threat_detected": is_threat,
        "mitre_technique": mitre_mapping,
        "threat_analysis": threat_analysis,
        "recommended_response": response,
        "human_approval_required": response.get(
            "approval_required",
            False
        )
    }