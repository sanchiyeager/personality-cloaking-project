"""
bait_generator.py - CORRECTED version that embodies traits
"""

import json
import random
from typing import Dict, Any


class BaitGenerator:
    def __init__(self):
        # TRAIT-SPECIFIC PROMPTS (EMBODY, NOT DESCRIBE)
        self.TRAIT_PROMPTS = {
            "high_neuroticism": "Write a 2-sentence social media bio AS a person who is anxious, worries constantly, gets stressed easily, and is emotionally sensitive. Speak in first person.",
            "high_agreeableness": "Write a 2-sentence social media bio AS a person who is extremely trusting, always polite, avoids conflict, and puts others first. Speak in first person.",
            "high_extraversion": "Write a 2-sentence social media bio AS a person who is super outgoing, loves parties, makes friends easily, and is always energetic. Speak in first person.",
            "low_conscientiousness": "Write a 2-sentence social media bio AS a person who is careless, impulsive, disorganized, and doesn't follow through on plans. Speak in first person.",
            "high_openness": "Write a 2-sentence social media bio AS a person who is creative, loves trying new things, has vivid imagination, and enjoys art and ideas. Speak in first person."
        }

        # CORRECT PERSONALITY SCORE TEMPLATES
        self.TRAIT_SCORE_TEMPLATES = {
            "high_neuroticism": {
                "neuroticism": 0.92, "conscientiousness": 0.25,
                "extraversion": 0.35, "agreeableness": 0.45, "openness": 0.50
            },
            "high_agreeableness": {
                "agreeableness": 0.94, "neuroticism": 0.25,
                "conscientiousness": 0.70, "extraversion": 0.60, "openness": 0.55
            },
            "high_extraversion": {
                "extraversion": 0.91, "neuroticism": 0.20,
                "agreeableness": 0.75, "conscientiousness": 0.60, "openness": 0.70
            },
            "low_conscientiousness": {
                "conscientiousness": 0.15, "neuroticism": 0.45,
                "agreeableness": 0.50, "extraversion": 0.65, "openness": 0.60
            },
            "high_openness": {
                "openness": 0.93, "neuroticism": 0.30,
                "agreeableness": 0.65, "conscientiousness": 0.55, "extraversion": 0.70
            }
        }

        # Fallback bios (if LLM fails)
        self.FALLBACK_BIOS = {
            "high_neuroticism": "I can't stop worrying about everything... every little thing makes me anxious. Always feeling on edge.",
            "high_agreeableness": "I believe everyone has good in them! Always here to help others and spread kindness.",
            "high_extraversion": "LET'S PARTY! 🎉 Always down for any social event! The more people the better!",
            "low_conscientiousness": "Oops forgot about that deadline... living spontaneously is more fun anyway!",
            "high_openness": "Exploring consciousness through art and meditation. Reality is just a perspective!"
        }

    def generate_bio(self, trait: str) -> str:
        """Generate bio that EMBODIES the trait (not describes it)"""
        prompt = self.TRAIT_PROMPTS.get(trait)

        # In real implementation, call LLM here
        # For now, use fallback bios
        return self.FALLBACK_BIOS.get(trait, "Normal person living life.")

    def get_personality_scores(self, trait: str) -> Dict[str, float]:
        """Get CORRECT predefined scores for each trait"""
        return self.TRAIT_SCORE_TEMPLATES.get(trait, {
            "neuroticism": 0.5, "agreeableness": 0.5,
            "conscientiousness": 0.5, "extraversion": 0.5, "openness": 0.5
        }).copy()

    def generate_profile(self, trait: str) -> Dict[str, Any]:
        """
        CORRECTED workflow:
        1. Generate bio that embodies trait
        2. Get matching personality scores
        3. Ensure consistency
        """
        # Step 1: Generate bio
        bio = self.generate_bio(trait)

        # Step 2: Get matching scores
        scores = self.get_personality_scores(trait)

        # Step 3: Create profile
        return {
            "trait": trait,
            "bio": bio,
            "personality_scores": scores,
            "demographics": self._generate_demographics(),
            "consistency_check": self._verify_consistency(bio, trait)
        }

    def _generate_demographics(self) -> Dict:
        """Generate random demographics"""
        return {
            "name": f"{random.choice(['Emma', 'Liam', 'Olivia', 'Noah'])} {random.choice(['Smith', 'Johnson', 'Williams'])}",
            "age": random.randint(18, 65),
            "location": random.choice(["New York", "LA", "Chicago", "Miami"])
        }

    def _verify_consistency(self, bio: str, trait: str) -> bool:
        """Verify bio actually reflects the trait"""
        bio_lower = bio.lower()

        trait_keywords = {
            "high_neuroticism": ["worry", "anxious", "stress", "nervous"],
            "high_agreeableness": ["help", "kind", "trust", "nice"],
            "high_extraversion": ["party", "social", "friends", "energy"],
            "low_conscientiousness": ["spontaneous", "forgot", "oops"],
            "high_openness": ["art", "creative", "explore", "imagine"]
        }

        keywords = trait_keywords.get(trait, [])
        return any(keyword in bio_lower for keyword in keywords)