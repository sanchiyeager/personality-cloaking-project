#Poonam's work


from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class PersonalityResponse(BaseModel):
    bio: str
    personality: dict

@app.post("/generate_bait_profile")
def generate_bait_profile():
    bio_templates = [
        "I love trying out new food trucks...",
        "Design lead by day...",
        "Graduate student in CS...",
        "Freelance photographer..."
    ]

    personality = {
        "openness": round(random.uniform(0.2, 0.95), 2),
        "conscientiousness": round(random.uniform(0.1, 0.9), 2),
        "extraversion": round(random.uniform(0.05, 0.9), 2),
        "agreeableness": round(random.uniform(0.15, 0.95), 2),
        "neuroticism": round(random.uniform(0.05, 0.85), 2)
    }

    return {"bio": random.choice(bio_templates), "personality": personality}
