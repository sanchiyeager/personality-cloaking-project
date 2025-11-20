# main.py
import sys, requests, logging
from typing import Optional, Dict, Any
from core.models import BaitProfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

class ProjectJanusOrchestrator:
    def __init__(self):
        self.components = {
            'bait_generator': False,
            'database': False,
            'frontend': False
        }
        self._setup_components()
    
    def _setup_components(self):
        """Test if all components are available"""
        try:
            from core import bait_generator
            self.bait_generator = bait_generator
            self.components['bait_generator'] = True
            logger.info("✅ Bait generator connected")
        except ImportError as e:
            logger.warning("❌ Bait generator not available: %s", e)
            self.bait_generator = None
        
        try:
            from core import database_module
            self.database = database_module
            self.components['database'] = True
            logger.info("✅ Database module connected")
        except ImportError as e:
            logger.warning("❌ Database module not available: %s", e)
            self.database = None
    
    def generate_bait_profile(self, trait: str) -> Optional[BaitProfile]:
        """Generate a bait profile using Poonam's component"""
        if not self.components['bait_generator']:
            logger.error("Bait generator not available")
            return self._create_fallback_profile(trait)
        
        try:
            raw_profile = self.bait_generator.generate_bait_profile(trait)
            
            profile = BaitProfile(
                bio=raw_profile.get('bio', ''),
                personality=raw_profile.get('scores', {}),
                target_trait=trait
            )
            
            logger.info("🎣 Generated bait profile for trait: %s", trait)
            return profile
            
        except Exception as e:
            logger.error("Error generating profile: %s", e)
            return self._create_fallback_profile(trait)
    
    def _create_fallback_profile(self, trait: str) -> BaitProfile:
        """Create a fallback profile when components fail"""
        fallback_bios = {
            "high_neuroticism": "I feel constantly worried about everything in my life. The smallest things make me anxious.",
            "high_agreeableness": "I love helping others and always try to see the best in people. Trust comes easily to me.",
            "low_conscientiousness": "I go with the flow and don't worry too much about planning. Life's more fun that way!"
        }
        
        return BaitProfile(
            bio=fallback_bios.get(trait, "A person looking to connect with others."),
            personality={
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5
            },
            target_trait=trait
        )
    
    def save_profile(self, profile: BaitProfile) -> bool:
        """Save profile using Harsh's database component"""
        if not self.components['database']:
            logger.warning("Database not available - profile not saved")
            return False
        
        try:
            result = self.database.save_profile(profile.to_dict())
            logger.info("💾 Profile saved to database")
            return True
        except Exception as e:
            logger.error("Error saving to database: %s", e)
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all integrated components"""
        return {
            'components': self.components,
            'ready': all(self.components.values()),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def run_demo(self):
        """Run a complete demo of the system"""
        print("\n" + "="*50)
        print("🚀 PROJECT JANUS - SYSTEM DEMO")
        print("="*50)
        
        status = self.get_system_status()
        print(f"System Status: {status}")
        
        # Test with different personality traits
        test_traits = ["high_neuroticism", "high_agreeableness", "low_conscientiousness"]
        
        for trait in test_traits:
            print(f"\n--- Testing: {trait} ---")
            profile = self.generate_bait_profile(trait)
            
            if profile:
                print(f"Bio: {profile.bio}")
                print(f"Scores: {profile.personality}")
                
                # Try to save
                if self.save_profile(profile):
                    print("✅ Saved to database")
                else:
                    print("⚠️  Could not save to database")
            else:
                print("❌ Failed to generate profile")

# Global instance
janus = ProjectJanusOrchestrator()

if __name__ == "__main__":
    janus.run_demo()