from pathlib import Path

import joblib
from sklearn.ensemble import IsolationForest


MODEL_PATH = Path(__file__).resolve().parent / "anomaly_model.joblib"


class TelemetryAnomalyDetector:

    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
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

        return {
            "is_anomaly": bool(prediction == -1),
            "anomaly_score": float(score)
        }

    def save(self) -> None:
        joblib.dump(self.model, MODEL_PATH)

    def load(self) -> None:
        self.model = joblib.load(MODEL_PATH)
        self.trained = True