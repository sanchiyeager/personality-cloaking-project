"""
bait_generator.py - Generates fake profiles with consistent personality traits
"""

import random
import json
from typing import Dict, Any
import openai  # or your LLM API of choice

# Configuration
LLM_MODEL = "gpt-3.5-turbo"  # or "gpt-4" for better quality


class BaitGenerator:
    def __init__(self, api_key: str = None):
        if api_key:
            openai.api_key = api_key

        # Personality score templates for each trait
        self.TRAIT_SCORE_TEMPLATES = {
            "high_neuroticism": {
                "neuroticism": 0.92,
                "conscientiousness": 0.25,
                "extraversion": 0.35,
                "agreeableness": 0.45,
                "openness": 0.50
            },
            "high_agreeableness": {
                "agreeableness": 0.94,
                "neuroticism": 0.25,
                "conscientiousness": 0.70,
                "extraversion": 0.60,
                "openness": 0.55
            },
            "high_extraversion": {
                "extraversion": 0.91,
                "neuroticism": 0.20,
                "agreeableness": 0.75,
                "conscientiousness": 0.60,
                "openness": 0.70
            },
            "low_conscientiousness": {
                "conscientiousness": 0.15,
                "neuroticism": 0.45,
                "agreeableness": 0.50,
                "extraversion": 0.65,
                "openness": 0.60
            },
            "high_openness": {
                "openness": 0.93,
                "neuroticism": 0.30,
                "agreeableness": 0.65,
                "conscientiousness": 0.55,
                "extraversion": 0.70
            },
            "average": {
                "neuroticism": 0.50,
                "agreeableness": 0.50,
                "conscientiousness": 0.50,
                "extraversion": 0.50,
                "openness": 0.50
            }
        }

        # Trait-specific bio generation prompts
        self.TRAIT_PROMPTS = {
            "high_neuroticism": (
                "Write a short 2-sentence social media bio from the perspective of someone who: "
                "is anxious and worries constantly, feels stressed easily, is emotionally sensitive "
                "and insecure, often overthinking things. Show don't tell - express through their words."
            ),
            "high_agreeableness": (
                "Write a short 2-sentence social media bio from the perspective of someone who: "
                "is extremely trusting and polite, avoids conflict at all costs, puts others first "
                "always, believes the best in people. Show don't tell - express through their words."
            ),
            "high_extraversion": (
                "Write a short 2-sentence social media bio from the perspective of someone who: "
                "is super outgoing and energetic, loves parties and social events, makes friends "
                "easily, is always up for adventures. Show don't tell - express through their words."
            ),
            "low_conscientiousness": (
                "Write a short 2-sentence social media bio from the perspective of someone who: "
                "is careless and disorganized, acts on impulse, doesn't follow through on plans, "
                "lives in the moment without thinking. Show don't tell - express through their words."
            ),
            "high_openness": (
                "Write a short 2-sentence social media bio from the perspective of someone who: "
                "is creative and imaginative, loves trying new experiences, enjoys art and philosophy, "
                "has vivid dreams and ideas. Show don't tell - express through their words."
            ),
            "average": (
                "Write a short 2-sentence social media bio for a normal person with average personality traits."
            )
        }

    def generate_bio(self, trait: str) -> str:
        """Generate a bio that embodies (not describes) the personality trait."""
        prompt = self.TRAIT_PROMPTS.get(trait, self.TRAIT_PROMPTS["average"])

        try:
            # Using OpenAI API (you can replace with your preferred LLM)
            response = openai.ChatCompletion.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are writing social media bios from different personality perspectives."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            bio = response.choices[0].message.content.strip()
            return bio
        except Exception as e:
            # Fallback bios if API fails
            fallback_bios = {
                "high_neuroticism": "I keep overthinking everything... is that normal? Always feeling anxious about what comes next.",
                "high_agreeableness": "Just here to spread kindness! Always willing to help others and see the good in everyone.",
                "high_extraversion": "LET'S GOOO! 🎉 Always down for a party or adventure! Hit me up for any social event!",
                "low_conscientiousness": "Oops forgot to update this... living spontaneously! Plans are boring anyway.",
                "high_openness": "Exploring consciousness through art and psychedelics. Reality is just one perspective among many.",
                "average": "Just living life day by day. Enjoying time with friends and family."
            }
            return fallback_bios.get(trait, "Normal person living a normal life.")

    def get_personality_scores(self, trait: str) -> Dict[str, float]:
        """Get predefined personality scores for the given trait."""
        return self.TRAIT_SCORE_TEMPLATES.get(trait, self.TRAIT_SCORE_TEMPLATES["average"]).copy()

    def generate_demographics(self) -> Dict[str, Any]:
        """Generate random demographic information."""
        first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Oliver", "Sophia", "Elijah", "Isabella", "Lucas"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                      "Martinez"]

        age = random.randint(18, 65)
        interests = random.sample([
            "reading", "gaming", "hiking", "cooking", "photography",
            "music", "travel", "yoga", "movies", "technology"
        ], 3)

        return {
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "age": age,
            "interests": interests,
            "location": random.choice(["New York", "Los Angeles", "Chicago", "Miami", "Austin"]),
            "occupation": random.choice([
                "Marketing Specialist", "Software Developer", "Teacher",
                "Nurse", "Graphic Designer", "Sales Representative"
            ])
        }

    def generate_profile(self, trait: str) -> Dict[str, Any]:
        """
        Generate a complete fake profile with consistent personality.

        Args:
            trait: One of ["high_neuroticism", "high_agreeableness",
                          "high_extraversion", "low_conscientiousness",
                          "high_openness", "average"]

        Returns:
            Dictionary containing complete profile
        """
        # Generate bio that embodies the trait
        bio = self.generate_bio(trait)

        # Get personality scores for this trait
        scores = self.get_personality_scores(trait)

        # Generate demographics
        demographics = self.generate_demographics()

        # Create complete profile
        profile = {
            "trait": trait,
            "bio": bio,
            "personality_scores": scores,
            "demographics": demographics,
            "creation_date": "2024-03-15"  # You can make this dynamic
        }

        return profile

    def batch_generate_profiles(self, n: int = 10) -> list:
        """Generate multiple profiles with random traits."""
        traits = list(self.TRAIT_SCORE_TEMPLATES.keys())
        profiles = []

        for _ in range(n):
            trait = random.choice(traits)
            profile = self.generate_profile(trait)
            profiles.append(profile)

        return profiles

    def save_profiles(self, profiles: list, filename: str = "generated_profiles.json"):
        """Save generated profiles to JSON file."""
        with open(filename, 'w') as f:
            json.dump(profiles, f, indent=2)
        print(f"Saved {len(profiles)} profiles to {filename}")

    def verify_profile_consistency(self, profile: Dict[str, Any]) -> bool:
        """
        Verify that the bio actually reflects the claimed personality trait.
        This is a simplified version - you should implement actual NLP analysis.
        """
        trait = profile["trait"]
        bio = profile["bio"].lower()

        # Simple keyword verification (you should use your ML model here)
        trait_keywords = {
            "high_neuroticism": ["anxious", "worry", "stress", "nervous", "overthink"],
            "high_agreeableness": ["kind", "help", "trust", "good", "nice", "polite"],
            "high_extraversion": ["party", "social", "energy", "friends", "outgoing", "fun"],
            "low_conscientiousness": ["spontaneous", "moment", "forgot", "plans", "boring"],
            "high_openness": ["art", "creative", "imagine", "explore", "dream", "consciousness"]
        }

        keywords = trait_keywords.get(trait, [])
        if keywords:
            # Check if any keywords appear in bio
            matches = [kw for kw in keywords if kw in bio]
            return len(matches) > 0

        return True  # For "average" trait


# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = BaitGenerator()

    # Generate a neurotic profile
    neurotic_profile = generator.generate_profile("high_neuroticism")
    print("Neurotic Profile:")
    print(f"Bio: {neurotic_profile['bio']}")
    print(f"Scores: {neurotic_profile['personality_scores']}")

    # Generate multiple profiles
    profiles = generator.batch_generate_profiles(3)
    generator.save_profiles(profiles)