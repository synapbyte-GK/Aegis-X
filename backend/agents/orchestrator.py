from analysis.security_analyzer import analyze_security_event
from agents.investigation_agent import investigate_event
from agents.correlation_agent import run_correlation
from agents.response_agent import run_response_agent
from agents.soc_commander import soc_command
from agents.report_agent import generate_report


def run_orchestrator(
    event_type: str,
    severity: str,
    message: str,
    related_events: list[dict] | None = None
) -> dict:

    # 1. Core security analysis
    security_analysis = analyze_security_event(
        event_type=event_type,
        severity=severity,
        message=message
    )

    # 2. Investigation agent
    investigation = investigate_event(
        security_analysis
    )

    # 3. Correlation agent
    correlation_events = related_events or [
        {
            "device_id": "UNKNOWN",
            "is_threat": security_analysis.get(
                "is_threat",
                False
            )
        }
    ]

    correlation = run_correlation(
        correlation_events
    )

    # 4. Response agent
    response = run_response_agent(
        security_analysis
    )

    # 5. SOC Commander
    soc_input = {
        **security_analysis,
        "response_recommendation": response
    }

    soc_decision = soc_command(
        soc_input
    )

    # 6. Final security report
    report = generate_report(
        security_analysis=security_analysis,
        investigation=investigation,
        soc_decision=soc_decision
    )

    return {
        "security_analysis": security_analysis,
        "investigation": investigation,
        "correlation": correlation,
        "response": response,
        "soc_decision": soc_decision,
        "report": report
    }