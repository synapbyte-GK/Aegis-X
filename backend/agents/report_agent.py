def generate_report(
    security_analysis: dict,
    investigation: dict,
    soc_decision: dict
) -> dict:

    mitre = security_analysis.get(
        "mitre_mapping",
        {}
    )

    return {
        "report_title": "Aegis-X Security Incident Report",
        "risk_level": security_analysis.get(
            "risk_level",
            "UNKNOWN"
        ),
        "threat_detected": security_analysis.get(
            "is_threat",
            False
        ),
        "mitre_technique": mitre,
        "investigation_status": investigation.get(
            "investigation_status",
            "UNKNOWN"
        ),
        "findings": investigation.get(
            "findings",
            []
        ),
        "soc_decision": soc_decision.get(
            "decision",
            "UNKNOWN"
        ),
        "priority": soc_decision.get(
            "priority",
            "UNKNOWN"
        ),
        "recommended_response": soc_decision.get(
            "recommended_response",
            {}
        ),
        "human_approval_required": soc_decision.get(
            "human_approval_required",
            False
        )
    }