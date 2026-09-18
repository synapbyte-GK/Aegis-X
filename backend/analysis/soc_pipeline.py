from analysis.security_analyzer import analyze_security_event
from agents.soc_commander import soc_command


def run_soc_pipeline(
    event_type: str,
    severity: str,
    message: str
) -> dict:

    security_analysis = analyze_security_event(
        event_type=event_type,
        severity=severity,
        message=message
    )

    soc_decision = soc_command(
        security_analysis
    )

    return {
        "security_analysis": security_analysis,
        "soc_decision": soc_decision
    }