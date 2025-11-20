from fastapi import FastAPI
from pydantic import BaseModel
from core.bait_generator import generate_bait_profile

app = FastAPI()   # <-- This is the ASGI app. MUST exist.

class TraitRequest(BaseModel):
    trait: str

@app.post("/generate_bait_profile")
def generate_bait_profile_api(request: TraitRequest):
    result = generate_bait_profile(request.trait)
    return result

@app.get("/status")
def status():
    return {"status": "ok"}
