FROM python:3.11-slim

WORKDIR /app

COPY app/ /app/app/
COPY logs/ /app/logs/

RUN mkdir -p /app/logs

CMD ["python", "app/generator.py"]
