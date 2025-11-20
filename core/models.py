#Data models


from dataclasses import dataclass
from typing import Dict

@dataclass
class BaitProfile:
    bio: str
    personality: Dict[str, float]  # Big Five scores
    target_trait: str = ""
    scam_type: str = ""
    
    def to_dict(self):
        return {
            "bio": self.bio,
            "personality": self.personality,
            "target_trait": self.target_trait,
            "scam_type": self.scam_type
        }