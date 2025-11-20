# main.py - COMPLETE WORKING VERSION WITH FALLBACKS
import sys
import logging
import sqlite3
from typing import Optional, Dict, Any
from dataclasses import dataclass
import random

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
        """Test if team components are available"""
        # Test Poonam's component
        try:
            from core import bait_generator
            self.bait_generator = bait_generator
            self.components['bait_generator'] = True
            logger.info("✅ Poonam's bait generator connected")
        except ImportError as e:
            logger.warning("❌ Poonam's bait generator not available - using fallback")
            self.bait_generator = None
        
        # Test Harsh's component  
        try:
            from core import database_module
            self.database = database_module
            self.components['database'] = True
            logger.info("✅ Harsh's database module connected")
        except ImportError as e:
            logger.warning("❌ Harsh's database module not available - using fallback")
            self.database = None
    
    def _setup_database(self):
        """Create database table if it doesn't exist"""
        try:
            conn = sqlite3.connect('profiles.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bio TEXT NOT NULL,
                    openness REAL CHECK (openness BETWEEN 0 AND 1),
                    conscientiousness REAL CHECK (conscientiousness BETWEEN 0 AND 1),
                    extraversion REAL CHECK (extraversion BETWEEN 0 AND 1),
                    agreeableness REAL CHECK (agreeableness BETWEEN 0 AND 1),
                    neuroticism REAL CHECK (neuroticism BETWEEN 0 AND 1),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("✅ Database table ready")
        except Exception as e:
            logger.warning("❌ Could not setup database: %s", e)
    
    def _fallback_bait_generator(self, trait: str) -> BaitProfile:
        """Fallback bait profile generator when Poonam's module isn't ready"""
        targeted_profiles = {
            "high_neuroticism": {
                "bio": "I feel constantly anxious about everything. My mind races with worries and worst-case scenarios all day long. I can't seem to relax.",
                "scores": {"openness": 0.3, "conscientiousness": 0.6, "extraversion": 0.2, "agreeableness": 0.4, "neuroticism": 0.95},
                "scam_type": "Investment Scams (FOMO)"
            },
            "high_agreeableness": {
                "bio": "I always see the best in people and trust others easily. Helping strangers brings me genuine joy and I believe everyone has good intentions.",
                "scores": {"openness": 0.7, "conscientiousness": 0.5, "extraversion": 0.6, "agreeableness": 0.92, "neuroticism": 0.3},
                "scam_type": "Romance Scams"
            },
            "low_conscientiousness": {
                "bio": "Why plan when you can be spontaneous? Rules are meant to be broken and I love taking risks. Life's too short for careful planning!",
                "scores": {"openness": 0.8, "conscientiousness": 0.15, "extraversion": 0.7, "agreeableness": 0.5, "neuroticism": 0.4},
                "scam_type": "Fake Gift Scams"
            },
            "high_openness": {
                "bio": "I'm fascinated by new technologies and unconventional ideas. Always experimenting with the latest apps and digital trends.",
                "scores": {"openness": 0.9, "conscientiousness": 0.4, "extraversion": 0.5, "agreeableness": 0.6, "neuroticism": 0.3},
                "scam_type": "Tech Support Scams"
            }
        }
        
        profile_data = targeted_profiles.get(trait, {
            "bio": "Just someone looking to connect with others online.",
            "scores": {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
            "scam_type": "General Phishing"
        })
        
        return BaitProfile(
            bio=profile_data["bio"],
            personality=profile_data["scores"],
            target_trait=trait,
            scam_type=profile_data["scam_type"]
        )
    
    def _fallback_save_profile(self, profile: BaitProfile) -> bool:
        """Fallback database save when Harsh's module isn't ready"""
        try:
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
            return True
        except Exception as e:
            logger.error("Fallback database error: %s", e)
            return False
    
    def generate_bait_profile(self, trait: str) -> Optional[BaitProfile]:
        """Generate bait profile - uses Poonam's module or fallback"""
        if self.components['bait_generator'] and self.bait_generator:
            try:
                # Try to use Poonam's function
                raw_profile = self.bait_generator.generate_bait_profile(trait)
                profile = BaitProfile(
                    bio=raw_profile.get('bio', ''),
                    personality=raw_profile.get('scores', {}),
                    target_trait=trait
                )
                logger.info("🎣 Used Poonam's generator for: %s", trait)
                return profile
            except Exception as e:
                logger.error("Poonam's generator failed: %s", e)
                # Fallback to our generator
                return self._fallback_bait_generator(trait)
        else:
            # Use our fallback generator
            return self._fallback_bait_generator(trait)
    
    def save_profile(self, profile: BaitProfile) -> bool:
        """Save profile - uses Harsh's module or fallback"""
        if self.components['database'] and self.database:
            try:
                result = self.database.save_profile(profile.to_dict())
                logger.info("💾 Used Harsh's database module")
                return True
            except Exception as e:
                logger.error("Harsh's database failed: %s", e)
                # Fallback to our database
                return self._fallback_save_profile(profile)
        else:
            # Use our fallback database
            return self._fallback_save_profile(profile)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all components"""
        return {
            'components': self.components,
            'ready': all(self.components.values()),
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'message': 'System operational with fallbacks' if not all(self.components.values()) else 'All components connected!'
        }
    
    def run_demo(self):
        """Run complete system demo"""
        print("\n" + "="*50)
        print("🚀 PROJECT JANUS - FULL SYSTEM DEMO")
        print("="*50)
        
        status = self.get_system_status()
        print(f"System Status: {status}")
        
        # Test all personality traits
        test_traits = ["high_neuroticism", "high_agreeableness", "low_conscientiousness", "high_openness"]
        
        for trait in test_traits:
            print(f"\n--- Testing: {trait} ---")
            profile = self.generate_bait_profile(trait)
            
            if profile:
                print(f"🎯 Target: {profile.scam_type}")
                print(f"📝 Bio: {profile.bio}")
                print(f"📊 Scores: {profile.personality}")
                
                # Save to database
                if self.save_profile(profile):
                    print("✅ Saved to database")
                else:
                    print("❌ Failed to save")
            else:
                print("❌ Failed to generate profile")
        
        print(f"\n🎉 Demo completed! Check 'profiles.db' for saved profiles.")

# Global instance
janus = ProjectJanusOrchestrator()

if __name__ == "__main__":
    janus.run_demo()