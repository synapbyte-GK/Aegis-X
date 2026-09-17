def map_to_attack(event_type: str, message: str) -> dict:
    event_type = event_type.lower()
    message = message.lower()

    if event_type == "brute_force" or "brute force" in message:
        return {
            "technique_id": "T1110",
            "technique_name": "Brute Force"
        }

    if event_type == "port_scan" or "scan" in message:
        return {
            "technique_id": "T1046",
            "technique_name": "Network Service Scanning"
        }

    if event_type == "unauthorized_access" or "unauthorized" in message:
        return {
            "technique_id": "T1078",
            "technique_name": "Valid Accounts"
        }

    if event_type == "malware" or "malware" in message:
        return {
            "technique_id": "T1204",
            "technique_name": "User Execution"
        }

    return {
        "technique_id": None,
        "technique_name": "Unknown"
    }