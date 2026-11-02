# CTEM Demo Store container image - TRAINING / LAB USE ONLY.
# Contains two intentional, non-destructive misconfigurations for IaC/container
# scanning demonstrations (see docs/security-scenarios.md):
#   CTEM-IAC-01 - container runs as root (no USER instruction)
#   CTEM-IAC-02 - no HEALTHCHECK instruction
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CTEM_HOST=0.0.0.0 \
    CTEM_PORT=8080

WORKDIR /app

COPY requirements.txt requirements-demo-sca.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY ctem_demo ./ctem_demo

EXPOSE 8080

CMD ["python", "app.py"]
