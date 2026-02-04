"""
core/chat_engine.py - CORRECTED version using ALL personality scores
"""

import json
import random
from typing import Dict, List, Optional


class ChatEngine:
    def __init__(self, model_path: str = None):
        self.model_path = model_path

    def generate_chat_response(self, personality_scores: Dict[str, float],
                               message: str, chat_history: List = None) -> str:
        """
        CORRECTED: Uses ALL 5 personality dimensions to influence response

        Args:
            personality_scores: ALL 5 traits (neuroticism, agreeableness, 
                               conscientiousness, extraversion, openness)
            message: Incoming scam message
            chat_history: Previous messages
        """
        # Extract ALL scores
        neuro = personality_scores.get('neuroticism', 0.5)
        agree = personality_scores.get('agreeableness', 0.5)
        consc = personality_scores.get('conscientiousness', 0.5)
        extra = personality_scores.get('extraversion', 0.5)
        openn = personality_scores.get('openness', 0.5)

        # Build response based on COMBINATION of all traits
        response_parts = []

        # 1. NEUROTICISM influences emotional tone
        if neuro > 0.7:
            anxious_phrases = ["I'm really worried about this...",
                               "This makes me so anxious...",
                               "I don't know what to do, I'm stressed..."]
            response_parts.append(random.choice(anxious_phrases))
        elif neuro < 0.3:
            calm_phrases = ["I'm not worried about this.",
                            "Everything will be fine.",
                            "No need to stress."]
            response_parts.append(random.choice(calm_phrases))

        # 2. AGREEABLENESS influences trust/compliance
        if agree > 0.7:
            trusting_phrases = ["Of course I'll help!",
                                "You seem very trustworthy!",
                                "I believe you completely!"]
            response_parts.append(random.choice(trusting_phrases))
        elif agree < 0.3:
            skeptical_phrases = ["I'm not sure about this...",
                                 "Why should I trust you?",
                                 "This seems suspicious."]
            response_parts.append(random.choice(skeptical_phrases))

        # 3. CONSCIENTIOUSNESS influences detail/organization
        if consc > 0.7:
            careful_phrases = ["Let me think about this carefully...",
                               "I need to check the details...",
                               "I should research this properly..."]
            response_parts.append(random.choice(careful_phrases))
        elif consc < 0.3:
            careless_phrases = ["Whatever, let's just do it!",
                                "No need to overthink!",
                                "Details don't matter."]
            response_parts.append(random.choice(careless_phrases))

        # 4. EXTRAVERSION influences enthusiasm
        if extra > 0.7:
            enthusiastic_phrases = ["This is exciting!! 😄",
                                    "Yesss let's do this!",
                                    "Wow that sounds amazing!"]
            response_parts.append(random.choice(enthusiastic_phrases))
        elif extra < 0.3:
            reserved_phrases = ["Okay.", "I see.", "Interesting."]
            response_parts.append(random.choice(reserved_phrases))

        # 5. OPENNESS influences creativity
        if openn > 0.7:
            creative_phrases = ["What an interesting idea!",
                                "This opens new possibilities!",
                                "I love exploring new things like this!"]
            response_parts.append(random.choice(creative_phrases))

        # Combine all influences
        if not response_parts:
            response_parts.append("Tell me more about this.")

        response = " ".join(response_parts)

        # Adjust style based on combined traits
        if extra > 0.7:
            response = response.rstrip('.!') + '!'
        if neuro > 0.7:
            response = response.rstrip('!.') + '...'
        if consc < 0.3 and len(response.split()) > 10:
            # Shorten if low conscientiousness
            response = " ".join(response.split()[:8]) + "..."

        return response

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