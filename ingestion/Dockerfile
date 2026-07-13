FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core ./core
COPY *.py ./
COPY sources ./sources

# Pensado para correr como Job/CronJob de k8s, no como servicio long-running.
CMD ["python", "run.py"]
