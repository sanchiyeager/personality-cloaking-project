"""
core/chat_engine.py - Context-aware, varied personality responses
"""

import random
from typing import Dict, List, Optional


# Per-trait response pools keyed by message intent
# Each pool has many options so replies don't repeat
_RESPONSES = {
    "high_neuroticism": {
        "greeting":   ["Oh hi... I wasn't expecting anyone to message me 😟",
                       "Hey... hope everything's okay?",
                       "Hi, is something wrong? You seem urgent.",
                       "Hello... I'm a bit nervous, what's this about?"],
        "money":      ["Oh no, money stuff really stresses me out...",
                       "I don't know... financial things make me so anxious.",
                       "I'd need to think about this a lot, I'm already panicking.",
                       "This is making my heart race, I'm not sure I can do this."],
        "urgent":     ["Wait wait wait — I need a moment, this is too much!",
                       "Please slow down, I can't handle pressure like this...",
                       "I'm freaking out a little, can you explain more slowly?",
                       "Urgent?! That word alone stresses me out..."],
        "prize":      ["Really? That sounds too good to be true and now I'm worried...",
                       "I don't know if I should believe this, what if it's a trap?",
                       "A prize? I'd be too scared to claim it honestly.",
                       "My anxiety is telling me something's off here..."],
        "default":    ["I'm not sure how to feel about this...",
                       "This is making me overthink everything.",
                       "Can you explain more? I'm getting anxious.",
                       "I keep going back and forth on this, I'm so stressed.",
                       "I don't know... something feels off and I can't relax.",
                       "Let me think... actually I'm too worried to think straight."],
    },
    "high_agreeableness": {
        "greeting":   ["Hi there! So lovely to hear from you 😊",
                       "Hello! Always happy to chat!",
                       "Hey! What can I do for you today?"],
        "money":      ["Of course, I'd love to help however I can!",
                       "Sure, just tell me what you need and I'll do my best.",
                       "I trust you, let's figure this out together!"],
        "urgent":     ["Oh of course, I'll help right away!",
                       "No worries, I'm here for you!",
                       "Absolutely, whatever you need!"],
        "prize":      ["Oh wow, that's so exciting! I'd love to claim it!",
                       "Really?! That's so kind, thank you so much!",
                       "I believe you! What do I need to do?"],
        "default":    ["That sounds wonderful, I'm happy to help!",
                       "Of course! I trust you completely.",
                       "Sure, whatever you think is best!",
                       "I'm always here if you need anything 😊",
                       "You seem really genuine, I appreciate that.",
                       "I don't want to cause any trouble, I'll go along with it."],
    },
    "high_extraversion": {
        "greeting":   ["HEYYY!! 😄 What's up!!",
                       "Omg hi!! So glad you reached out!",
                       "Hey hey hey! What's the vibe today?!"],
        "money":      ["Ooh money talk, let's gooo! Tell me everything!",
                       "YES I'm in, sounds like an adventure!",
                       "Money?! I love it, what's the deal?!"],
        "urgent":     ["Ooh urgent?! I LOVE the energy, let's do this!!",
                       "Say less, I'm already hyped!",
                       "Let's GOOO, what do you need?!"],
        "prize":      ["NO WAY I WON?! 🎉🎉 This is the best day ever!!",
                       "YESSS let's celebrate!! How do I claim it?!",
                       "I'm literally screaming right now, this is amazing!!"],
        "default":    ["That sounds SO fun, tell me more!",
                       "Omg yes, I'm totally down for this!",
                       "This is giving me so much energy, I love it!",
                       "Let's do it!! Life's too short to say no!",
                       "I'm already telling my friends about this lol",
                       "Sounds like a vibe, I'm in 😄"],
    },
    "low_conscientiousness": {
        "greeting":   ["oh hey lol what's up",
                       "yo, sup",
                       "heyyy, what do you want lol"],
        "money":      ["idk man, sure why not lol",
                       "whatever, sounds fine to me",
                       "eh I'll figure it out later"],
        "urgent":     ["lol okay okay chill, I'll do it",
                       "sure whatever, not a big deal",
                       "fine fine, I'll get to it eventually"],
        "prize":      ["lol okay cool, how do I get it",
                       "sure I'll take it, why not",
                       "sounds random but okay lmao"],
        "default":    ["idk, maybe? I haven't really thought about it",
                       "sure lol, whatever you say",
                       "I'll deal with it later tbh",
                       "eh, doesn't really matter to me",
                       "lol okay fine",
                       "I mean... sure? I guess?"],
    },
    "high_openness": {
        "greeting":   ["Hello! What fascinating thing brings you here today?",
                       "Hi! I love meeting new people with new ideas.",
                       "Hey there, what's on your mind?"],
        "money":      ["Interesting... what's the philosophy behind this offer?",
                       "Money is just energy, tell me more about the concept.",
                       "I'm curious about the mechanics of this, explain?"],
        "urgent":     ["Urgency is an interesting construct... but okay, what is it?",
                       "I'm intrigued, what's the deeper story here?",
                       "Tell me everything, I love a good mystery."],
        "prize":      ["How curious! What are the odds? I'd love to understand the system.",
                       "Fascinating — what's the story behind this prize?",
                       "I'm open to exploring this, tell me more!"],
        "default":    ["That's a really interesting perspective.",
                       "I've never thought about it that way before.",
                       "Tell me more, I find this genuinely fascinating.",
                       "What an unusual idea — I'm intrigued.",
                       "I love exploring new concepts like this.",
                       "This opens up so many questions for me."],
    },
    "average": {
        "greeting":   ["Hi, how can I help?",
                       "Hello there.",
                       "Hey, what's up?"],
        "money":      ["Okay, what exactly are you offering?",
                       "I'd need more details before deciding.",
                       "That depends, what's involved?"],
        "urgent":     ["Alright, what do you need?",
                       "Okay, I'm listening.",
                       "Sure, what's going on?"],
        "prize":      ["Interesting. What do I need to do?",
                       "Okay, tell me more.",
                       "I'd want to know the details first."],
        "default":    ["I see, tell me more.",
                       "Okay, what's this about?",
                       "Sure, go on.",
                       "Alright, I'm listening.",
                       "That's something to think about.",
                       "Makes sense, what's next?"],
    },
}

# Trait score → pool key mapping
_TRAIT_MAP = [
    ("high_neuroticism",     lambda s: s.get("neuroticism", 0) > 0.7),
    ("high_agreeableness",   lambda s: s.get("agreeableness", 0) > 0.7),
    ("high_extraversion",    lambda s: s.get("extraversion", 0) > 0.7),
    ("low_conscientiousness",lambda s: s.get("conscientiousness", 0) < 0.3),
    ("high_openness",        lambda s: s.get("openness", 0) > 0.7),
]


def _detect_intent(message: str) -> str:
    """Classify the incoming message into a rough intent bucket."""
    m = message.lower()
    greetings = ["hi", "hey", "hello", "sup", "yo", "howdy", "hiya", "good morning",
                 "good evening", "what's up", "whats up"]
    if any(g in m for g in greetings) and len(m.split()) <= 5:
        return "greeting"
    if any(w in m for w in ["money", "transfer", "send", "pay", "cash", "fund",
                             "account", "dollar", "rupee", "fee", "cost", "price"]):
        return "money"
    if any(w in m for w in ["urgent", "immediately", "now", "asap", "hurry",
                             "quick", "fast", "emergency", "suspended", "hacked"]):
        return "urgent"
    if any(w in m for w in ["won", "winner", "prize", "congratulations", "selected",
                             "reward", "gift", "free", "lucky"]):
        return "prize"
    return "default"


def _dominant_trait(scores: Dict[str, float]) -> str:
    for trait_key, check in _TRAIT_MAP:
        if check(scores):
            return trait_key
    return "average"


class ChatEngine:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        # Track last used response per trait+intent to avoid immediate repeats
        self._last_used: Dict[str, str] = {}

    def generate_chat_response(self, personality_scores: Dict[str, float],
                               message: str, chat_history: List = None) -> str:
        trait = _dominant_trait(personality_scores)
        intent = _detect_intent(message)
        pool = _RESPONSES[trait][intent]

        # Avoid repeating the last response for this trait+intent combo
        cache_key = f"{trait}:{intent}"
        last = self._last_used.get(cache_key)
        choices = [r for r in pool if r != last] or pool
        reply = random.choice(choices)
        self._last_used[cache_key] = reply
        return reply

    def analyze_personality_from_text(self, text: str) -> Dict[str, float]:
        """
        Analyze text to get personality scores
        (You should train an ML model for this)
        """
        # Simplified version - in reality, use your trained model
        text_lower = text.lower()

        scores = {
            "neuroticism": 0.5,
            "agreeableness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "openness": 0.5
        }

        # Simple keyword analysis
        if any(word in text_lower for word in ["worry", "anxious", "stress"]):
            scores["neuroticism"] = 0.8
        if any(word in text_lower for word in ["help", "kind", "trust"]):
            scores["agreeableness"] = 0.8
        if any(word in text_lower for word in ["party", "social", "fun"]):
            scores["extraversion"] = 0.8
        if any(word in text_lower for word in ["art", "creative", "imagine"]):
            scores["openness"] = 0.8

        return scores


# Global instance and function for imports
chat_engine = ChatEngine()


def generate_chat_response(personality_scores, message, chat_history=None):
    return chat_engine.generate_chat_response(personality_scores, message, chat_history)