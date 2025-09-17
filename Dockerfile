FROM python:3.12.3-slim as build-env

ARG ENVIRONMENT

ENV TELEGRAM_TOKEN=${TELEGRAM_TOKEN}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]