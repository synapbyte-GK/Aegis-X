from fastapi import APIRouter
from ml.anomaly_detector import TelemetryAnomalyDetector


router = APIRouter()

model = TelemetryAnomalyDetector()


@router.post("/ml-anomaly/train")
def train_model(data: list[dict]):
    model.train(data)

    return {
        "trained": True,
        "message": "Anomaly detection model trained successfully"
    }


@router.post("/ml-anomaly/predict")
def predict_anomaly(data: dict):
    result = model.predict(data)

    return {
        "device_id": data.get("device_id"),
        **result
    }