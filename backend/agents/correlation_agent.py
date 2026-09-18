from correlation.correlation_engine import correlate_events


def run_correlation(events: list[dict]) -> dict:

    return correlate_events(events)