from fastapi import FastAPI, Request, HTTPException
import os

from rate_limiter import RateLimiter
from logging_config import get_logger
from safety import safety_check, SAFE_WATERMARK

from scam_templates import generate_template as generate_message

app = FastAPI(title="Backend Scam Simulation API (Safe)")

limiter = RateLimiter(max_requests=10, window_seconds=60)
logger = get_logger()

API_TOKEN = os.getenv("API_TOKEN", "")

@app.get("/simulate/{kind}")
async def simulate(kind: str, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    if API_TOKEN:
        token = request.headers.get("x-api-token", "")
        if token != API_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")

    ok, retry = limiter.allow(client_ip)
    if not ok:
        logger.info(f"RATE_LIMIT | ip={client_ip} retry_after={retry}s")
        raise HTTPException(status_code=429, detail=f"Too many requests. Retry after {retry}s")

    try:
        data = generate_message(kind)
    except Exception as e:
        logger.info(f"GEN_ERROR | ip={client_ip} kind={kind} | err={str(e)}")
        raise HTTPException(status_code=400, detail=f"Generator error: {str(e)}")

    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail=f"Generator returned {type(data)} not dict")

    subject = data.get("subject", "")
    message = data.get("message", "")

    if SAFE_WATERMARK not in subject:
        subject = f"{SAFE_WATERMARK} {subject}".strip()
    if SAFE_WATERMARK not in message:
        message = f"{SAFE_WATERMARK}\n{message}".strip()

    combined = subject + "\n" + message

    ok2, reason = safety_check(combined)
    if not ok2:
        logger.info(f"BLOCKED | ip={client_ip} kind={kind} | reason={reason}")
        raise HTTPException(status_code=400, detail=f"Blocked: {reason}")

    logger.info(f"OK | ip={client_ip} kind={kind}")
    return {"type": kind, "subject": subject, "message": message}
