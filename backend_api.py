"""
backend_api.py - API for integrating all components
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import json
from bait_generator import BaitGenerator
from chat_engine import ChatEngine

app = FastAPI(title="Personality Cloaking API")

# Initialize components
bait_generator = BaitGenerator()
chat_engine = ChatEngine()  # Or load fine-tuned model


class ProfileRequest(BaseModel):
    trait: str = "high_neuroticism"
    count: int = 1


class ChatRequest(BaseModel):
    personality_scores: Dict[str, float]
    message: str
    chat_history: List[Dict] = []


class ProfileResponse(BaseModel):
    profiles: List[Dict[str, Any]]


class ChatResponse(BaseModel):
    response: str
    analyzed_scores: Dict[str, float] = None


@app.post("/generate_profiles", response_model=ProfileResponse)
async def generate_profiles(request: ProfileRequest):
    """Generate fake profiles with specific personality traits."""
    try:
        if request.count == 1:
            profile = bait_generator.generate_profile(request.trait)
            profiles = [profile]
        else:
            profiles = []
            for _ in range(request.count):
                profile = bait_generator.generate_profile(request.trait)
                profiles.append(profile)

        return ProfileResponse(profiles=profiles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_chat_response", response_model=ChatResponse)
async def generate_chat_response(request: ChatRequest):
    """Generate personality-consistent chat response."""
    try:
        response = chat_engine.generate_chat_response(
            personality_scores=request.personality_scores,
            message=request.message,
            chat_history=request.chat_history
        )

        # Optional: Analyze the response's personality
        analyzed_scores = chat_engine.analyze_response_personality(response)

        return ChatResponse(
            response=response,
            analyzed_scores=analyzed_scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/traits")
async def get_available_traits():
    """Get list of available personality traits."""
    traits = [
        "high_neuroticism",
        "high_agreeableness",
        "high_extraversion",
        "low_conscientiousness",
        "high_openness",
        "average"
    ]
    return {"traits": traits}


@app.get("/test_chat")
async def test_chat():
    """Test endpoint with example chat."""
    neurotic_scores = {
        "neuroticism": 0.92,
        "agreeableness": 0.45,
        "conscientiousness": 0.25,
        "extraversion": 0.35,
        "openness": 0.50
    }

    test_message = "Your bank account has been compromised! Click here immediately!"

    response = chat_engine.generate_chat_response(neurotic_scores, test_message)

    return {
        "personality_scores": neurotic_scores,
        "test_message": test_message,
        "generated_response": response
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "personality_cloaking_api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)