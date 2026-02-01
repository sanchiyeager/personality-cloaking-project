# main.py - COMPLETE WORKING VERSION WITH CHAT ENGINE INTEGRATION

import sys
import logging
import sqlite3
from typing import Optional, Dict, Any
from dataclasses import dataclass
import random

# ✅ IMPORT CHAT ENGINE
from core.chat_engine import generate_chat_response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")


@dataclass
class BaitProfile:
    bio: str
    personality: Dict[str, float]
    target_trait: str = ""
    scam_type: str = ""

    def to_dict(self):
        return {
            "bio": self.bio,
            "personality": self.personality,
            "target_trait": self.target_trait,
            "scam_type": self.scam_type
        }


class ProjectJanusOrchestrator:
    def __init__(self):
        self.components = {
            'bait_generator': False,
            'database': False,
            'frontend': False
        }
        self._setup_components()
        self._setup_database()

    def _setup_components(self):
        try:
            from core import bait_generator
            self.bait_generator = bait_generator
            self.components['bait_generator'] = True
            logger.info("✅ Poonam's bait generator connected")
        except ImportError:
            logger.warning("❌ Poonam's bait generator not available - using fallback")
            self.bait_generator = None

        try:
            from core import database_module
            self.database = database_module
            self.components['database'] = True
            logger.info("✅ Harsh's database module connected")
        except ImportError:
            logger.warning("❌ Harsh's database module not available - using fallback")
            self.database = None

    def _setup_database(self):
        conn = sqlite3.connect('profiles.db')
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS profiles
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           bio
                           TEXT,
                           openness
                           REAL,
                           conscientiousness
                           REAL,
                           extraversion
                           REAL,
                           agreeableness
                           REAL,
                           neuroticism
                           REAL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        conn.commit()
        conn.close()
        logger.info("✅ Database ready")

    def _fallback_bait_generator(self, trait: str) -> BaitProfile:
        profiles = {
            "high_neuroticism": (
                "I constantly worry about my safety and finances.",
                {"openness": 0.3, "conscientiousness": 0.6, "extraversion": 0.2, "agreeableness": 0.4,
                 "neuroticism": 0.95},
                "Investment Scam"
            ),
            "high_agreeableness": (
                "I trust people easily and enjoy helping others.",
                {"openness": 0.7, "conscientiousness": 0.5, "extraversion": 0.6, "agreeableness": 0.92,
                 "neuroticism": 0.3},
                "Romance Scam"
            ),
            "low_conscientiousness": (
                "I act on impulse and avoid planning.",
                {"openness": 0.8, "conscientiousness": 0.15, "extraversion": 0.7, "agreeableness": 0.5,
                 "neuroticism": 0.4},
                "Gift Scam"
            ),
            "high_openness": (
                "I love trying new tech and online tools.",
                {"openness": 0.9, "conscientiousness": 0.4, "extraversion": 0.5, "agreeableness": 0.6,
                 "neuroticism": 0.3},
                "Tech Support Scam"
            )
        }

        bio, scores, scam_type = profiles.get(
            trait,
            ("Normal online user.",
             {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
             "Phishing")
        )

        return BaitProfile(bio=bio, personality=scores, target_trait=trait, scam_type=scam_type)

    def save_profile(self, profile: BaitProfile):
        conn = sqlite3.connect('profiles.db')
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO profiles (bio, openness, conscientiousness, extraversion, agreeableness, neuroticism)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (
                           profile.bio,
                           profile.personality['openness'],
                           profile.personality['conscientiousness'],
                           profile.personality['extraversion'],
                           profile.personality['agreeableness'],
                           profile.personality['neuroticism']
                       ))
        conn.commit()
        conn.close()

    def run_demo(self):
        print("\n🚀 PROJECT JANUS – CHAT + BAIT DEMO\n")

        scam_message = "URGENT! Your bank account is blocked. Verify OTP immediately."

        traits = ["high_neuroticism", "high_agreeableness", "low_conscientiousness", "high_openness"]

        for trait in traits:
            print("=" * 60)
            profile = self._fallback_bait_generator(trait)

            print(f"🎯 Trait: {trait}")
            print(f"📝 Bio: {profile.bio}")
            print(f"📩 Scam Message: {scam_message}")

            response = generate_chat_response(profile.personality, scam_message)

            print(f"🤖 Victim Response: {response}")

            self.save_profile(profile)
            print("💾 Profile saved\n")

        print("✅ Demo finished. Check profiles.db")


# Run system
if __name__ == "__main__":
    janus = ProjectJanusOrchestrator()
    janus.run_demo()
