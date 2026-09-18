def investigate_event(security_analysis: dict) -> dict:

    is_threat = security_analysis.get("is_threat", False)
    risk_level = security_analysis.get("risk_level", "UNKNOWN")

    mitre_mapping = security_analysis.get(
        "mitre_mapping",
        {}
    )

    if not is_threat:
        return {
            "investigation_status": "NO_THREAT",
            "findings": [
                "No significant threat was detected."
            ],
            "risk_level": risk_level
        }

    findings = [
        "Suspicious security activity was detected.",
        f"Risk level assessed as {risk_level}."
    ]

    technique_id = mitre_mapping.get("technique_id")
    technique_name = mitre_mapping.get("technique_name")

    if technique_id:
        findings.append(
            f"Activity mapped to MITRE ATT&CK "
            f"{technique_id} ({technique_name})."
        )

    return {
        "investigation_status": "THREAT_CONFIRMED",
        "findings": findings,
        "risk_level": risk_level,
        "mitre_technique": mitre_mapping
    }