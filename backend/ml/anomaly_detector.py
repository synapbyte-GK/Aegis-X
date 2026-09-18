from pathlib import Path

import joblib
from sklearn.ensemble import IsolationForest


MODEL_PATH = Path(__file__).resolve().parent / "anomaly_model.joblib"


class TelemetryAnomalyDetector:

    def __init__(self):
        self.model = IsolationForest(
            contamination=0.02,
            random_state=42
        )

        self.trained = False

        if MODEL_PATH.exists():
            self.load()

    def train(self, telemetry_data: list[dict]) -> None:

        features = [
            [
                item.get("temperature", 0),
                item.get("humidity", 0),
                item.get("cpu_usage", 0)
            ]
            for item in telemetry_data
        ]

        if len(features) < 2:
            raise ValueError(
                "At least 2 telemetry records are required"
            )

        self.model.fit(features)

        self.trained = True

        self.save()

    def _rule_based_anomaly(self, telemetry: dict) -> bool:
        temperature = float(
            telemetry.get("temperature", 0)
        )

        humidity = float(
            telemetry.get("humidity", 0)
        )

        cpu_usage = float(
            telemetry.get("cpu_usage", 0)
        )

        network_activity = str(
            telemetry.get("network_activity", "")
        ).lower()

        if temperature >= 60:
            return True

        if cpu_usage >= 80:
            return True

        if humidity < 20 or humidity > 80:
            return True

        if network_activity in {
            "suspicious",
            "malicious",
            "attack"
        }:
            return True

        return False

    def predict(self, telemetry: dict) -> dict:

        if not self.trained:
            raise RuntimeError(
                "Model must be trained before prediction"
            )

        features = [[
            telemetry.get("temperature", 0),
            telemetry.get("humidity", 0),
            telemetry.get("cpu_usage", 0)
        ]]

        prediction = self.model.predict(features)[0]

        score = self.model.decision_function(features)[0]

        ml_anomaly = prediction == -1

        rule_anomaly = self._rule_based_anomaly(
            telemetry
        )

        # Hybrid decision:
        # Clear security/safety rule violations are anomalies.
        # ML output is retained for additional analysis.
        is_anomaly = (
            rule_anomaly
            or (
                ml_anomaly
                and (
                    float(telemetry.get("temperature", 0)) >= 50
                    or float(telemetry.get("cpu_usage", 0)) >= 70
                    or str(
                        telemetry.get(
                            "network_activity",
                            ""
                        )
                    ).lower() != "normal"
                )
            )
        )

        return {
            "is_anomaly": bool(is_anomaly),
            "ml_prediction": bool(ml_anomaly),
            "rule_anomaly": bool(rule_anomaly),
            "anomaly_score": float(score)
        }

    def save(self) -> None:
        joblib.dump(self.model, MODEL_PATH)

    def load(self) -> None:
        self.model = joblib.load(MODEL_PATH)
        self.trained = True