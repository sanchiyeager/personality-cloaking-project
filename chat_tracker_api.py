"""
Chat Tracker API Endpoints

Provides REST API endpoints for:
- Saving conversations
- Retrieving conversation data
- Managing chat sessions
- Accessing engagement metrics and attack classifications
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from core.database_module import (
    create_conversation, add_message, end_conversation,
    get_conversation, get_profile_conversations,
    get_engagement_metrics, get_attack_classifications,
    save_engagement_metrics, save_attack_classification
)
from core.engagement_tracker import EngagementTracker, ConversationAnalyzer
from core.models import ChatMessage, Conversation, EngagementMetric, AttackClassification
from logging_config import get_logger

logger = get_logger()

# ==================== Pydantic Models ====================

class ConversationRequest(BaseModel):
    """Request to create a new conversation"""
    profile_id: int
    attacker_id: str
    scam_type: Optional[str] = None


class MessageRequest(BaseModel):
    """Request to add a message to a conversation"""
    sender_type: str  # 'attacker' or 'bait_profile'
    message_text: str


class ConversationSummaryResponse(BaseModel):
    """Response with conversation summary"""
    conversation_id: int
    profile_id: int
    attacker_id: str
    message_count: int
    engagement: dict
    attack_analysis: dict


class EngagementMetricsResponse(BaseModel):
    """Response with engagement metrics"""
    conversation_id: int
    response_time_avg: Optional[float]
    response_time_min: Optional[float]
    response_time_max: Optional[float]
    message_length_avg: float
    message_count: int
    sentiment_avg: float


class AttackClassificationResponse(BaseModel):
    """Response with attack classification"""
    attack_type: str
    confidence: float
    techniques_detected: List[str]
    severity_level: str


class MessageResponse(BaseModel):
    """Response after adding a message"""
    id: int
    conversation_id: int
    sender_type: str
    message_text: str
    sent_at: str


class HighRiskConversationResponse(BaseModel):
    """Response with high-risk conversation info"""
    conversation_id: int
    attack_type: str
    severity: str
    confidence: float
    techniques: List[str]


# ==================== API Routes ====================

class ChatTrackerAPI:
    """Chat Tracker API endpoints"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """Setup all API routes"""
        
        # Conversation Management
        self.app.post("/api/v1/conversations", response_model=dict)(self.create_conversation)
        self.app.get("/api/v1/conversations/{conversation_id}", response_model=dict)(self.get_conversation_endpoint)
        self.app.get("/api/v1/profiles/{profile_id}/conversations", response_model=list)(self.get_profile_conversations_endpoint)
        self.app.post("/api/v1/conversations/{conversation_id}/end", response_model=dict)(self.end_conversation_endpoint)
        
        # Message Management
        self.app.post("/api/v1/conversations/{conversation_id}/messages", response_model=MessageResponse)(self.add_message_endpoint)
        self.app.get("/api/v1/conversations/{conversation_id}/messages", response_model=list)(self.get_messages_endpoint)
        
        # Engagement Metrics
        self.app.get("/api/v1/conversations/{conversation_id}/metrics", response_model=dict)(self.get_metrics_endpoint)
        self.app.post("/api/v1/conversations/{conversation_id}/calculate-metrics")(self.calculate_metrics_endpoint)
        
        # Attack Classification
        self.app.get("/api/v1/conversations/{conversation_id}/classification", response_model=dict)(self.get_classification_endpoint)
        self.app.post("/api/v1/conversations/{conversation_id}/classify")(self.classify_attack_endpoint)
        
        # Conversation Analysis
        self.app.get("/api/v1/conversations/{conversation_id}/summary", response_model=dict)(self.get_conversation_summary_endpoint)
        self.app.get("/api/v1/profiles/{profile_id}/high-risk", response_model=list)(self.get_high_risk_conversations_endpoint)
        
        # Health Check
        self.app.get("/api/v1/health")(self.health_check)
    
    # ==================== Conversation Management ====================
    
    async def create_conversation(self, request: ConversationRequest):
        """Create a new conversation"""
        try:
            conv_id = create_conversation(
                profile_id=request.profile_id,
                attacker_id=request.attacker_id,
                scam_type=request.scam_type
            )
            
            if not conv_id:
                raise HTTPException(status_code=400, detail="Failed to create conversation")
            
            logger.info(f"CONVERSATION_CREATED | conv_id={conv_id} profile_id={request.profile_id} attacker_id={request.attacker_id}")
            
            return {
                "conversation_id": conv_id,
                "status": "created",
                "profile_id": request.profile_id,
                "attacker_id": request.attacker_id
            }
        except Exception as e:
            logger.error(f"CREATE_CONVERSATION_ERROR | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")
    
    async def get_conversation_endpoint(self, conversation_id: int):
        """Get conversation details"""
        try:
            conversation = get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            return conversation.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"GET_CONVERSATION_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")
    
    async def get_profile_conversations_endpoint(self, profile_id: int):
        """Get all conversations for a profile"""
        try:
            conversations = get_profile_conversations(profile_id)
            return [conv.to_dict() for conv in conversations]
        except Exception as e:
            logger.error(f"GET_PROFILE_CONVERSATIONS_ERROR | profile_id={profile_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")
    
    async def end_conversation_endpoint(self, conversation_id: int):
        """End a conversation"""
        try:
            success = end_conversation(conversation_id)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to end conversation")
            
            logger.info(f"CONVERSATION_ENDED | conv_id={conversation_id}")
            
            return {"conversation_id": conversation_id, "status": "ended"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"END_CONVERSATION_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error ending conversation: {str(e)}")
    
    # ==================== Message Management ====================
    
    async def add_message_endpoint(self, conversation_id: int, request: MessageRequest):
        """Add a message to a conversation"""
        try:
            message = add_message(
                conversation_id=conversation_id,
                sender_type=request.sender_type,
                message_text=request.message_text
            )
            
            if not message:
                raise HTTPException(status_code=400, detail="Failed to add message")
            
            logger.info(f"MESSAGE_ADDED | conv_id={conversation_id} sender={request.sender_type} len={len(request.message_text)}")
            
            return MessageResponse(
                id=message.id,
                conversation_id=message.conversation_id,
                sender_type=message.sender_type,
                message_text=message.message_text,
                sent_at=message.sent_at.isoformat()
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ADD_MESSAGE_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")
    
    async def get_messages_endpoint(self, conversation_id: int, limit: int = 100, offset: int = 0):
        """Get messages from a conversation"""
        try:
            conversation = get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            messages = conversation.messages[offset:offset + limit]
            return [msg.to_dict() for msg in messages]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"GET_MESSAGES_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")
    
    # ==================== Engagement Metrics ====================
    
    async def get_metrics_endpoint(self, conversation_id: int):
        """Get engagement metrics for a conversation"""
        try:
            metrics = get_engagement_metrics(conversation_id)
            if not metrics:
                return {"message": "No metrics calculated yet"}
            
            return metrics.to_dict()
        except Exception as e:
            logger.error(f"GET_METRICS_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")
    
    async def calculate_metrics_endpoint(self, conversation_id: int, background_tasks: BackgroundTasks):
        """Calculate and save engagement metrics"""
        try:
            conversation = get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Calculate in background
            metrics = EngagementTracker.generate_engagement_metrics(conversation)
            background_tasks.add_task(save_engagement_metrics, metrics)
            
            logger.info(f"METRICS_CALCULATED | conv_id={conversation_id}")
            
            return {
                "conversation_id": conversation_id,
                "status": "calculating",
                "metrics": metrics.to_dict()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CALCULATE_METRICS_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")
    
    # ==================== Attack Classification ====================
    
    async def get_classification_endpoint(self, conversation_id: int):
        """Get attack classification for a conversation"""
        try:
            classifications = get_attack_classifications(conversation_id)
            if not classifications:
                return {"message": "No classification yet"}
            
            latest = classifications[0]
            return latest.to_dict()
        except Exception as e:
            logger.error(f"GET_CLASSIFICATION_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving classification: {str(e)}")
    
    async def classify_attack_endpoint(self, conversation_id: int, background_tasks: BackgroundTasks):
        """Classify attack type in a conversation"""
        try:
            conversation = get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Classify in background
            classification = EngagementTracker.classify_conversation_attack(conversation)
            background_tasks.add_task(save_attack_classification, classification)
            
            logger.info(f"ATTACK_CLASSIFIED | conv_id={conversation_id} type={classification.attack_type} severity={classification.severity_level}")
            
            return {
                "conversation_id": conversation_id,
                "status": "classified",
                "classification": classification.to_dict()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CLASSIFY_ATTACK_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error classifying attack: {str(e)}")
    
    # ==================== Conversation Analysis ====================
    
    async def get_conversation_summary_endpoint(self, conversation_id: int):
        """Get comprehensive conversation summary"""
        try:
            conversation = get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            summary = ConversationAnalyzer.get_conversation_summary(conversation)
            return summary
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"GET_SUMMARY_ERROR | conv_id={conversation_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
    
    async def get_high_risk_conversations_endpoint(self, profile_id: int):
        """Get high-risk conversations for a profile"""
        try:
            conversations = get_profile_conversations(profile_id)
            high_risk = ConversationAnalyzer.identify_high_risk_conversations(conversations)
            return high_risk
        except Exception as e:
            logger.error(f"GET_HIGH_RISK_ERROR | profile_id={profile_id} | {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error identifying high-risk conversations: {str(e)}")
    
    # ==================== Health Check ====================
    
    async def health_check(self):
        """API health check"""
        return {
            "status": "healthy",
            "service": "Chat Tracker API",
            "timestamp": datetime.now().isoformat()
        }


def setup_chat_tracker_api(app: FastAPI):
    """Initialize Chat Tracker API endpoints"""
    ChatTrackerAPI(app)
    logger.info("Chat Tracker API endpoints initialized")
