from detection.threat_analyzer import analyze_threat


def run_threat_analysis(security_analysis: dict) -> dict:

    return analyze_threat(
        event_type=security_analysis.get("event_type", ""),
        severity=security_analysis.get("severity", ""),
        risk_level=security_analysis.get("risk_level", "UNKNOWN"),
        is_threat=security_analysis.get("is_threat", False),
        mitre_mapping=security_analysis.get("mitre_mapping", {})
    )