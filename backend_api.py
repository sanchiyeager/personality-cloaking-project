from fastapi import FastAPI
from pydantic import BaseModel

# Existing import
from core.bait_generator import generate_bait_profile

# NEW import (Chatbot Response Engine)
from core.chat_engine import generate_chat_response


app = FastAPI()   # ASGI app


# ----------------------------
# Request Models
# ----------------------------

class TraitRequest(BaseModel):
    trait: str


class ChatRequest(BaseModel):
    personality_scores: dict
    message: str


# ----------------------------
# API Endpoints
# ----------------------------

@app.post("/generate_bait_profile")
def generate_bait_profile_api(request: TraitRequest):
    result = generate_bait_profile(request.trait)
    return result


@app.post("/generate_chat_response")
def generate_chat_response_api(request: ChatRequest):
    response = generate_chat_response(
        request.personality_scores,
        request.message
    )
    return {"response": response}


@app.get("/status")
def status():
    return {"status": "ok"}
