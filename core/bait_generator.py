# Poonam's work

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

# ===========================
# 1. LOAD PERSONALITY MODEL
# ===========================
tokenizer = AutoTokenizer.from_pretrained("vladinc/bigfive-regression-model")
model = AutoModelForSequenceClassification.from_pretrained("vladinc/bigfive-regression-model")

def get_personality_scores(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    scores = torch.softmax(outputs.logits, dim=1).tolist()[0]

    return {
        "openness": scores[0],
        "conscientiousness": scores[1],
        "extraversion": scores[2],
        "agreeableness": scores[3],
        "neuroticism": scores[4],
    }

# ===========================
# 2. BIO GENERATOR
# ===========================
bio_generator = pipeline("text-generation", model="distilgpt2")

def generate_bio_for_trait(trait):
    prompt = f"Write a short friendly social media bio for someone who has {trait}."
    result = bio_generator(prompt, max_length=60, num_return_sequences=1)
    return result[0]["generated_text"]


# ===========================
# 3. MAIN BAIT GENERATOR FUNCTION (REQUIRED BY FastAPI)
# ===========================
def generate_bait_profile(trait: str):
    """
    This is the function FastAPI will call.
    You MUST have this function or backend_api will crash.
    """

    # personality score for the given trait
    scores = get_personality_scores(trait)

    # generate a matching bio
    bio = generate_bio_for_trait(trait)

    return {
        "trait": trait,
        "scores": scores,
        "bio": bio
    }


    
