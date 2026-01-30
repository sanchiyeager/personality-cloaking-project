from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
import time

from scam_generator import generate_and_log

app = FastAPI(title="Scam Simulation API")

MIN_SECONDS_BETWEEN_CALLS = 3
_last_call = 0.0

class GenerateRequest(BaseModel):
    category: Literal["phishing", "romance", "investment"]
    target_personality: str = "default"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate(req: GenerateRequest):
    global _last_call
    now = time.time()

    if now - _last_call < MIN_SECONDS_BETWEEN_CALLS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        result = generate_and_log(req.category, req.target_personality)
        _last_call = now
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
