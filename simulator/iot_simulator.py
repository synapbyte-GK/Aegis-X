import json
import random
import time

import websocket


WS_URL = "ws://127.0.0.1:8002/ws/telemetry"

DEVICE_ID = "ESP32-001"

INTERVAL_SECONDS = 5


def generate_normal_telemetry():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(24, 32), 2),
        "humidity": round(random.uniform(40, 65), 2),
        "cpu_usage": round(random.uniform(10, 35), 2),
        "network_activity": "normal",
    }


def generate_anomaly_telemetry():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(70, 85), 2),
        "humidity": round(random.uniform(55, 70), 2),
        "cpu_usage": round(random.uniform(85, 99), 2),
        "network_activity": "suspicious",
    }


def main():
    print("Aegis-X IoT Simulator")
    print(f"Connecting to: {WS_URL}")

    ws = websocket.create_connection(
        WS_URL,
        timeout=20
    )

    print("WebSocket connected.")

    counter = 0

    try:
        while True:
            counter += 1

            # Every 5th reading simulates an anomaly
            if counter % 5 == 0:
                telemetry = generate_anomaly_telemetry()
                telemetry_type = "ANOMALY"
            else:
                telemetry = generate_normal_telemetry()
                telemetry_type = "NORMAL"

            ws.send(json.dumps(telemetry))

            response = json.loads(ws.recv())

            ml_anomaly = response.get(
                "ml_anomaly",
                {}
            )

            security_event = response.get(
                "security_event",
                {}
            )

            print()
            print(f"[{telemetry_type}] Telemetry sent:")
            print(
                f"Temperature: {telemetry['temperature']} °C"
            )
            print(
                f"Humidity: {telemetry['humidity']}%"
            )
            print(
                f"CPU: {telemetry['cpu_usage']}%"
            )
            print(
                f"Network: {telemetry['network_activity']}"
            )

            print(
                f"ML Anomaly: "
                f"{ml_anomaly.get('is_anomaly')}"
            )

            print(
                f"Security Event: "
                f"{security_event.get('event_type', 'none')}"
            )

            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")

    finally:
        ws.close()


if __name__ == "__main__":
    main()