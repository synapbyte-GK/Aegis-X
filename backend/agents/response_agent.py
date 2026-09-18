from response.response_recommender import recommend_response


def run_response_agent(security_analysis: dict) -> dict:

    return recommend_response(
        severity=security_analysis.get("severity", ""),
        risk_level=security_analysis.get("risk_level", "UNKNOWN"),
        is_threat=security_analysis.get("is_threat", False),
        mitre_mapping=security_analysis.get("mitre_mapping", {})
    )