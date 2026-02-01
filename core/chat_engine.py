from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Use pretrained DistilGPT-2 from Hugging Face Hub
tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
model = AutoModelForCausalLM.from_pretrained("distilgpt2")

# Personality flavor + signature phrases
PERSONALITY_FLAVOR = {
    "openness": (
        "I’m very curious and imaginative. I love exploring new ideas and perspectives. "
        "Let me think outside the box for this situation. "
    ),
    "conscientiousness": (
        "I’m precise, careful, and responsible. I like to plan and make sure everything is correct. "
        "Let’s approach this methodically. "
    ),
    "extraversion": (
        "I’m energetic, cheerful, and expressive! I love interacting with people. "
        "Yay! Let’s tackle this with enthusiasm! "
    ),
    "agreeableness": (
        "I’m friendly, empathetic, and cooperative. I always try to be supportive and polite. "
        "Sure thing! I’ll do my best to help. "
    ),
    "neuroticism": (
        "I’m easily worried, anxious, and sensitive. I tend to overthink problems and anticipate risks. "
        "Ugh… I’m so nervous about this! What if something goes wrong? "
    )
}


def generate_chat_response(personality_scores, message):
    # Pick dominant trait
    trait = max(personality_scores, key=personality_scores.get)

    # Get personality flavor
    flavor_text = PERSONALITY_FLAVOR.get(trait, "")

    # Build prompt
    prompt = f"{flavor_text}Incoming message: {message}\nResponse:"

    # Tokenize and generate response
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=120,
        do_sample=True,
        temperature=0.9,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove prompt to keep only chatbot reply
    reply = response.replace(prompt, "").strip()

    # Optional: truncate overly long or repeated output
    reply = ' '.join(reply.split()[:60])

    return reply
