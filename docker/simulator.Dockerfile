FROM python:3.14-slim

WORKDIR /app

COPY docker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY simulator ./simulator

CMD ["python", "simulator/iot_simulator.py"]