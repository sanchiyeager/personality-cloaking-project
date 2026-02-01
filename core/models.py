#Data models


from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

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


@dataclass
class ChatMessage:
    """Represents a single message in a conversation"""
    conversation_id: int
    sender_type: str  # 'bait_profile' or 'attacker'
    message_text: str
    sent_at: datetime = None
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.sent_at is None:
            self.sent_at = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_type": self.sender_type,
            "message_text": self.message_text,
            "sent_at": self.sent_at.isoformat() if isinstance(self.sent_at, datetime) else self.sent_at
        }


@dataclass
class Conversation:
    """Represents a conversation between a bait profile and an attacker"""
    profile_id: int
    attacker_id: str
    scam_type: str = None
    started_at: datetime = None
    ended_at: Optional[datetime] = None
    status: str = 'active'  # 'active', 'ended', 'archived'
    id: Optional[int] = None
    messages: List[ChatMessage] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.messages is None:
            self.messages = []
    
    def add_message(self, sender_type: str, message_text: str):
        """Add a message to the conversation"""
        message = ChatMessage(
            conversation_id=self.id,
            sender_type=sender_type,
            message_text=message_text
        )
        self.messages.append(message)
        return message
    
    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "attacker_id": self.attacker_id,
            "scam_type": self.scam_type,
            "started_at": self.started_at.isoformat() if isinstance(self.started_at, datetime) else self.started_at,
            "ended_at": self.ended_at.isoformat() if isinstance(self.ended_at, datetime) else self.ended_at,
            "status": self.status,
            "messages": [msg.to_dict() for msg in self.messages]
        }


@dataclass
class EngagementMetric:
    """Engagement metrics derived from a conversation"""
    conversation_id: int
    response_time_avg: float = None
    response_time_min: float = None
    response_time_max: float = None
    message_length_avg: float = None
    message_length_total: int = None
    message_count: int = None
    sentiment_avg: float = None
    sentiment_compound: float = None
    calculated_at: datetime = None
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.calculated_at is None:
            self.calculated_at = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "response_time_avg": self.response_time_avg,
            "response_time_min": self.response_time_min,
            "response_time_max": self.response_time_max,
            "message_length_avg": self.message_length_avg,
            "message_length_total": self.message_length_total,
            "message_count": self.message_count,
            "sentiment_avg": self.sentiment_avg,
            "sentiment_compound": self.sentiment_compound,
            "calculated_at": self.calculated_at.isoformat() if isinstance(self.calculated_at, datetime) else self.calculated_at
        }


@dataclass
class AttackClassification:
    """Classification of the type of attack/scam being attempted"""
    conversation_id: int
    attack_type: str  # e.g., 'romance_scam', 'phishing', 'financial_fraud', 'identity_theft'
    confidence: float  # 0.0 to 1.0
    techniques_detected: List[str] = None  # e.g., ['trust_building', 'urgency', 'verification_bypass']
    severity_level: str = 'medium'  # 'low', 'medium', 'high', 'critical'
    classified_at: datetime = None
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.techniques_detected is None:
            self.techniques_detected = []
        if self.classified_at is None:
            self.classified_at = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "attack_type": self.attack_type,
            "confidence": self.confidence,
            "techniques_detected": self.techniques_detected,
            "severity_level": self.severity_level,
            "classified_at": self.classified_at.isoformat() if isinstance(self.classified_at, datetime) else self.classified_at
        }
