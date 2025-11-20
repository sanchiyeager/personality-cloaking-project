# Poonam's work

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

# ===========================
# 1. LOAD BIG FIVE PERSONALITY MODEL
# ===========================
tokenizer = AutoTokenizer.from_pretrained("vladinc/bigfive-regression-model")
model = AutoModelForSequenceClassification.from_pretrained("vladinc/bigfive-regression-model")

def get_personality_scores(text):
    """
    Returns real personality scores from the Big Five model for a given text.
    """
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
# 2. BIO GENERATOR SETUP
# ===========================
bio_generator = pipeline("text-generation", model="distilgpt2")

def generate_bio_for_trait(trait):
    """
    Generates a short, friendly bio for a given personality trait.
    """
    prompt = f"Write a short friendly social media bio for someone who has {trait}."
    result = bio_generator(
        prompt,
        max_new_tokens=30,    # limit bio length
        num_return_sequences=1,
        do_sample=True,       # randomness for variety
        top_k=50,             # token selection limit
        top_p=0.95,           # nucleus sampling
        truncation=True       # explicitly truncate
    )
    bio = result[0]["generated_text"]

    # Keep only the first sentence
    bio = bio.split(".")[0].strip() + "."
    return bio

# ===========================
# 3. MAIN BAIT GENERATOR FUNCTION
# ===========================
def generate_bait_profile(trait: str):
    """
    Main function to generate a personality bio + real model scores.
    """
    # Optional: fallback text if trait not found
    fallback_text = "I am a normal person."

    # Get personality scores from model
    scores = get_personality_scores(fallback_text)

    # Generate matching short bio
    bio = generate_bio_for_trait(trait)

    return {
        "trait": trait,
        "scores": scores,
        "bio": bio
    }

# ===========================
# 4. TESTING (optional)
# ===========================
if __name__ == "__main__":
    traits = ["high_neuroticism", "high_openness", "low_conscientiousness"]
    for t in traits:
        print(generate_bait_profile(t))
