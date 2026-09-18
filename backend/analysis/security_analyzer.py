from detection.risk_engine import calculate_risk
from detection.threat_detector import detect_threat
from mitre.attack_mapper import map_to_attack
from detection.threat_analyzer import analyze_threat
from response.response_recommender import recommend_response


def analyze_security_event(
    event_type: str,
    severity: str,
    message: str
) -> dict:

    risk_level = calculate_risk(severity)

    is_threat = detect_threat(
        event_type,
        message
    )

    mitre_mapping = map_to_attack(
        event_type,
        message
    )

    threat_analysis = analyze_threat(
        event_type=event_type,
        severity=severity,
        risk_level=risk_level,
        is_threat=is_threat,
        mitre_mapping=mitre_mapping
    )

    response_recommendation = recommend_response(
        severity=severity,
        risk_level=risk_level,
        is_threat=is_threat,
        mitre_mapping=mitre_mapping
    )

    return {
        "event_type": event_type,
        "severity": severity,
        "risk_level": risk_level,
        "is_threat": is_threat,
        "mitre_mapping": mitre_mapping,
        "threat_analysis": threat_analysis,
        "response_recommendation": response_recommendation
    }