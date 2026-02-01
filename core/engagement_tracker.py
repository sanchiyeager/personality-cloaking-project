"""
Engagement Tracker Module

Analyzes chat conversations to calculate engagement metrics and classify attacks.
Computes:
- Response times (average, min, max)
- Message length statistics
- Sentiment analysis
- Attack classification and severity assessment
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
import statistics

# Try to import sentiment analyzer, fallback to basic scoring if not available
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

from models import ChatMessage, Conversation, EngagementMetric, AttackClassification


class EngagementTracker:
    """Calculate engagement metrics from conversations"""
    
    # Attack type keywords mapping
    ATTACK_KEYWORDS = {
        'romance_scam': ['love', 'miss you', 'sweetheart', 'marriage', 'relationship', 'meet', 'feelings', 'care'],
        'phishing': ['verify', 'confirm', 'click', 'password', 'account', 'urgent', 'action required', 'confirm identity'],
        'financial_fraud': ['investment', 'profit', 'return', 'fund', 'transaction', 'wire', 'payment', 'account number'],
        'identity_theft': ['ssn', 'social security', 'date of birth', 'mother', 'maiden name', 'verify identity', 'confirmation'],
        'prize_scam': ['won', 'winner', 'prize', 'claim', 'lottery', 'congratulations', 'lucky'],
        'tech_support': ['error', 'malware', 'virus', 'update', 'install', 'download', 'technical support', 'computer'],
        'employment_scam': ['job', 'hire', 'position', 'salary', 'work from home', 'urgent hire'],
    }
    
    @staticmethod
    def calculate_response_times(messages: List[ChatMessage]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate response time statistics (average, min, max) in seconds.
        Response time is measured as time between attacker message and bait response.
        """
        response_times = []
        
        for i in range(1, len(messages)):
            if messages[i].sender_type == 'bait_profile' and messages[i-1].sender_type == 'attacker':
                # Time between attacker message and bait response
                time_diff = messages[i].sent_at - messages[i-1].sent_at
                response_times.append(time_diff.total_seconds())
        
        if not response_times:
            return None, None, None
        
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        return avg_response_time, min_response_time, max_response_time
    
    @staticmethod
    def calculate_message_length_stats(messages: List[ChatMessage]) -> Tuple[float, int]:
        """
        Calculate average message length and total message count.
        Returns (average_length, total_length)
        """
        if not messages:
            return 0.0, 0
        
        total_length = sum(len(msg.message_text) for msg in messages)
        avg_length = total_length / len(messages)
        
        return avg_length, total_length
    
    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """
        Analyze sentiment of text.
        Returns a polarity score from -1.0 (negative) to 1.0 (positive)
        """
        if HAS_TEXTBLOB:
            analysis = TextBlob(text)
            return analysis.sentiment.polarity
        else:
            # Fallback: simple keyword-based sentiment
            positive_words = ['good', 'great', 'love', 'happy', 'excellent', 'wonderful', 'best']
            negative_words = ['bad', 'hate', 'sad', 'terrible', 'worst', 'horrible', 'angry']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            total = pos_count + neg_count
            if total == 0:
                return 0.0
            
            return (pos_count - neg_count) / total
    
    @staticmethod
    def calculate_conversation_sentiment(messages: List[ChatMessage]) -> float:
        """
        Calculate average sentiment across all messages in conversation.
        Returns compound sentiment score from -1.0 to 1.0
        """
        if not messages:
            return 0.0
        
        sentiments = [EngagementTracker.analyze_sentiment(msg.message_text) for msg in messages]
        return statistics.mean(sentiments) if sentiments else 0.0
    
    @staticmethod
    def classify_attack(messages: List[ChatMessage]) -> Tuple[str, float, List[str]]:
        """
        Classify the type of attack based on message content.
        Returns (attack_type, confidence_score, detected_techniques)
        
        Confidence is 0.0-1.0 based on keyword matches
        """
        if not messages:
            return 'unknown', 0.0, []
        
        # Combine all messages into one text
        combined_text = ' '.join(msg.message_text.lower() for msg in messages)
        
        attack_scores = {}
        detected_keywords = {attack_type: [] for attack_type in EngagementTracker.ATTACK_KEYWORDS}
        
        # Score each attack type
        for attack_type, keywords in EngagementTracker.ATTACK_KEYWORDS.items():
            matches = 0
            for keyword in keywords:
                if keyword in combined_text:
                    matches += 1
                    detected_keywords[attack_type].append(keyword)
            
            # Calculate confidence based on keyword matches
            if len(keywords) > 0:
                confidence = matches / len(keywords)
                attack_scores[attack_type] = confidence
        
        if not attack_scores:
            return 'unknown', 0.0, []
        
        # Get the attack type with highest confidence
        best_attack = max(attack_scores, key=attack_scores.get)
        best_confidence = attack_scores[best_attack]
        techniques = list(set(detected_keywords[best_attack]))  # Remove duplicates
        
        return best_attack, best_confidence, techniques
    
    @staticmethod
    def determine_severity_level(confidence: float, attack_type: str) -> str:
        """
        Determine severity level based on attack type and confidence.
        Returns 'low', 'medium', 'high', or 'critical'
        """
        # Higher confidence = higher severity
        if confidence >= 0.8:
            severity = 'critical'
        elif confidence >= 0.6:
            severity = 'high'
        elif confidence >= 0.4:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Adjust based on attack type (some are inherently more severe)
        high_severity_attacks = ['financial_fraud', 'identity_theft']
        if attack_type in high_severity_attacks and severity == 'medium':
            severity = 'high'
        
        return severity
    
    @staticmethod
    def generate_engagement_metrics(conversation: Conversation) -> EngagementMetric:
        """
        Generate complete engagement metrics for a conversation.
        """
        messages = conversation.messages or []
        
        # Calculate all metrics
        avg_response, min_response, max_response = EngagementTracker.calculate_response_times(messages)
        avg_msg_len, total_msg_len = EngagementTracker.calculate_message_length_stats(messages)
        sentiment = EngagementTracker.calculate_conversation_sentiment(messages)
        
        metrics = EngagementMetric(
            conversation_id=conversation.id,
            response_time_avg=avg_response,
            response_time_min=min_response,
            response_time_max=max_response,
            message_length_avg=avg_msg_len,
            message_length_total=total_msg_len,
            message_count=len(messages),
            sentiment_avg=sentiment,
            sentiment_compound=sentiment
        )
        
        return metrics
    
    @staticmethod
    def classify_conversation_attack(conversation: Conversation) -> AttackClassification:
        """
        Classify the attack in a conversation.
        """
        messages = conversation.messages or []
        attack_type, confidence, techniques = EngagementTracker.classify_attack(messages)
        severity = EngagementTracker.determine_severity_level(confidence, attack_type)
        
        classification = AttackClassification(
            conversation_id=conversation.id,
            attack_type=attack_type,
            confidence=confidence,
            techniques_detected=techniques,
            severity_level=severity
        )
        
        return classification


class ConversationAnalyzer:
    """Comprehensive analysis of conversations"""
    
    @staticmethod
    def get_conversation_summary(conversation: Conversation) -> Dict:
        """
        Generate a summary of conversation metrics and classification.
        """
        metrics = EngagementTracker.generate_engagement_metrics(conversation)
        classification = EngagementTracker.classify_conversation_attack(conversation)
        
        return {
            'conversation_id': conversation.id,
            'profile_id': conversation.profile_id,
            'attacker_id': conversation.attacker_id,
            'duration': (conversation.ended_at - conversation.started_at).total_seconds() 
                       if conversation.ended_at else None,
            'message_count': metrics.message_count,
            'engagement': {
                'avg_response_time_seconds': metrics.response_time_avg,
                'min_response_time_seconds': metrics.response_time_min,
                'max_response_time_seconds': metrics.response_time_max,
                'avg_message_length': metrics.message_length_avg,
                'total_text_length': metrics.message_length_total,
                'sentiment_score': metrics.sentiment_avg,
            },
            'attack_analysis': {
                'attack_type': classification.attack_type,
                'confidence': classification.confidence,
                'severity_level': classification.severity_level,
                'techniques_detected': classification.techniques_detected,
            }
        }
    
    @staticmethod
    def compare_conversations(conversation1: Conversation, conversation2: Conversation) -> Dict:
        """
        Compare metrics between two conversations.
        """
        metrics1 = EngagementTracker.generate_engagement_metrics(conversation1)
        metrics2 = EngagementTracker.generate_engagement_metrics(conversation2)
        
        return {
            'conversation_1_id': conversation1.id,
            'conversation_2_id': conversation2.id,
            'message_count_diff': metrics2.message_count - metrics1.message_count,
            'response_time_diff': (metrics2.response_time_avg or 0) - (metrics1.response_time_avg or 0),
            'sentiment_diff': metrics2.sentiment_avg - metrics1.sentiment_avg,
            'avg_message_length_diff': metrics2.message_length_avg - metrics1.message_length_avg,
        }
    
    @staticmethod
    def identify_high_risk_conversations(conversations: List[Conversation]) -> List[Dict]:
        """
        Identify conversations with high-risk attack characteristics.
        """
        high_risk = []
        
        for conversation in conversations:
            classification = EngagementTracker.classify_conversation_attack(conversation)
            
            # Flag as high risk if severity is high or critical
            if classification.severity_level in ['high', 'critical']:
                high_risk.append({
                    'conversation_id': conversation.id,
                    'attack_type': classification.attack_type,
                    'severity': classification.severity_level,
                    'confidence': classification.confidence,
                    'techniques': classification.techniques_detected,
                })
        
        return sorted(high_risk, key=lambda x: x['confidence'], reverse=True)


class AnalyticsEngine:
    """Analytics for tracking bait profile success and attack patterns"""
    
    @staticmethod
    def calculate_profile_success_metrics(conversations: List[Conversation]) -> Dict:
        """
        Calculate success metrics for a bait profile.
        Success = ability to sustain conversations and gather threat intelligence
        """
        if not conversations:
            return {
                'total_conversations': 0,
                'active_conversations': 0,
                'ended_conversations': 0,
                'success_rate': 0.0,
                'avg_conversation_length': 0,
                'avg_engagement_time': 0.0,
                'total_messages': 0,
                'avg_response_time': None,
                'threat_capture_score': 0.0
            }
        
        active_count = sum(1 for c in conversations if c.status == 'active')
        ended_count = sum(1 for c in conversations if c.status == 'ended')
        
        total_messages = sum(len(c.messages) for c in conversations)
        avg_messages_per_conv = total_messages / len(conversations) if conversations else 0
        
        # Calculate engagement times
        engagement_times = []
        response_times = []
        
        for conversation in conversations:
            if conversation.messages and len(conversation.messages) > 1:
                start = conversation.messages[0].sent_at
                end = conversation.messages[-1].sent_at
                engagement_time = (end - start).total_seconds()
                engagement_times.append(engagement_time)
            
            if conversation.ended_at:
                duration = (conversation.ended_at - conversation.started_at).total_seconds()
                if duration > 0:
                    engagement_times.append(duration)
        
        avg_engagement = statistics.mean(engagement_times) if engagement_times else 0.0
        
        # Calculate response times
        for conversation in conversations:
            for i in range(1, len(conversation.messages)):
                if conversation.messages[i].sender_type == 'bait_profile' and \
                   conversation.messages[i-1].sender_type == 'attacker':
                    time_diff = conversation.messages[i].sent_at - conversation.messages[i-1].sent_at
                    response_times.append(time_diff.total_seconds())
        
        avg_response = statistics.mean(response_times) if response_times else None
        
        # Success rate: conversations that lasted more than 3 exchanges
        successful_conversations = sum(
            1 for c in conversations 
            if len(c.messages) >= 4  # At least 2 attacker messages + 2 bait responses
        )
        success_rate = successful_conversations / len(conversations) if conversations else 0.0
        
        # Threat capture score: how well profile captures threats (high severity, confidence)
        threat_score = 0.0
        threat_count = 0
        for conversation in conversations:
            classification = EngagementTracker.classify_conversation_attack(conversation)
            if classification.attack_type != 'unknown':
                # Score based on detection confidence and severity
                severity_multiplier = {
                    'low': 0.25,
                    'medium': 0.5,
                    'high': 0.75,
                    'critical': 1.0
                }
                severity_score = severity_multiplier.get(classification.severity_level, 0.0)
                threat_score += classification.confidence * severity_score
                threat_count += 1
        
        threat_capture_score = threat_score / threat_count if threat_count > 0 else 0.0
        
        return {
            'total_conversations': len(conversations),
            'active_conversations': active_count,
            'ended_conversations': ended_count,
            'success_rate': success_rate,
            'avg_conversation_length': avg_messages_per_conv,
            'avg_engagement_time': avg_engagement,
            'total_messages': total_messages,
            'avg_response_time': avg_response,
            'threat_capture_score': threat_capture_score
        }
    
    @staticmethod
    def rank_profiles_by_success(profile_conversations_map: Dict[int, List[Conversation]]) -> List[Dict]:
        """
        Rank bait profiles by success metrics.
        Returns sorted list of profiles with their metrics.
        
        Args:
            profile_conversations_map: Dict of profile_id -> list of conversations
        
        Returns:
            List of dicts with profile_id, metrics, and rank
        """
        profile_rankings = []
        
        for profile_id, conversations in profile_conversations_map.items():
            metrics = AnalyticsEngine.calculate_profile_success_metrics(conversations)
            
            # Calculate composite score
            success_weight = 0.3
            engagement_weight = 0.2
            threat_weight = 0.5
            
            composite_score = (
                metrics['success_rate'] * success_weight +
                (metrics['avg_conversation_length'] / 10) * engagement_weight +  # Normalize
                metrics['threat_capture_score'] * threat_weight
            )
            
            profile_rankings.append({
                'profile_id': profile_id,
                'composite_score': min(composite_score, 1.0),  # Cap at 1.0
                'metrics': metrics
            })
        
        # Sort by composite score descending
        return sorted(profile_rankings, key=lambda x: x['composite_score'], reverse=True)
    
    @staticmethod
    def get_attack_type_distribution(conversations: List[Conversation]) -> Dict[str, int]:
        """
        Get distribution of attack types across conversations.
        """
        distribution = {}
        
        for conversation in conversations:
            classification = EngagementTracker.classify_conversation_attack(conversation)
            attack_type = classification.attack_type
            distribution[attack_type] = distribution.get(attack_type, 0) + 1
        
        return distribution
    
    @staticmethod
    def get_severity_distribution(conversations: List[Conversation]) -> Dict[str, int]:
        """
        Get distribution of severity levels across conversations.
        """
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for conversation in conversations:
            classification = EngagementTracker.classify_conversation_attack(conversation)
            severity = classification.severity_level
            distribution[severity] = distribution.get(severity, 0) + 1
        
        return distribution
    
    @staticmethod
    def calculate_bait_effectiveness(profile_id: int, conversations: List[Conversation]) -> Dict:
        """
        Calculate how effective a bait profile is at attracting and engaging attackers.
        
        Returns metrics like:
        - Engagement rate (% of conversations with multiple exchanges)
        - Average conversation duration
        - Types of threats attracted
        - Response quality (sentiment, engagement)
        """
        if not conversations:
            return {'profile_id': profile_id, 'effectiveness': 0.0}
        
        # Engagement rate
        engaged_conversations = sum(
            1 for c in conversations 
            if len(c.messages) >= 4
        )
        engagement_rate = engaged_conversations / len(conversations) if conversations else 0.0
        
        # Attack diversity
        attack_distribution = AnalyticsEngine.get_attack_type_distribution(conversations)
        attack_diversity = len([v for v in attack_distribution.values() if v > 0])
        
        # Average duration
        durations = []
        for conversation in conversations:
            if conversation.ended_at:
                duration = (conversation.ended_at - conversation.started_at).total_seconds()
                durations.append(duration)
        
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # Sentiment analysis (more positive sentiment = more successful engagement)
        sentiments = []
        for conversation in conversations:
            sentiment = EngagementTracker.calculate_conversation_sentiment(conversation.messages)
            sentiments.append(sentiment)
        
        avg_sentiment = statistics.mean(sentiments) if sentiments else 0.0
        
        # Effectiveness score (0-1)
        # High engagement rate, diverse threats, longer conversations, positive sentiment
        effectiveness = (
            engagement_rate * 0.4 +
            (attack_diversity / 7) * 0.3 +  # 7 attack types total
            (avg_duration / 3600) * 0.2 +   # Normalize to hours
            ((avg_sentiment + 1) / 2) * 0.1  # Normalize sentiment to 0-1
        )
        effectiveness = min(effectiveness, 1.0)
        
        return {
            'profile_id': profile_id,
            'effectiveness': effectiveness,
            'engagement_rate': engagement_rate,
            'attack_diversity': attack_diversity,
            'avg_conversation_duration': avg_duration,
            'avg_sentiment': avg_sentiment,
            'total_conversations': len(conversations),
            'attack_distribution': attack_distribution,
            'severity_distribution': AnalyticsEngine.get_severity_distribution(conversations)
        }
    
    @staticmethod
    def identify_top_threat_attractors(profile_conversations_map: Dict[int, List[Conversation]], 
                                      top_n: int = 5) -> List[Dict]:
        """
        Identify the top N bait profiles that attract the most serious threats.
        """
        profile_threat_scores = []
        
        for profile_id, conversations in profile_conversations_map.items():
            threat_score = 0.0
            critical_count = 0
            
            for conversation in conversations:
                classification = EngagementTracker.classify_conversation_attack(conversation)
                
                severity_multiplier = {
                    'low': 0.1,
                    'medium': 0.3,
                    'high': 0.6,
                    'critical': 1.0
                }
                
                severity_score = severity_multiplier.get(classification.severity_level, 0.0)
                threat_score += classification.confidence * severity_score
                
                if classification.severity_level == 'critical':
                    critical_count += 1
            
            profile_threat_scores.append({
                'profile_id': profile_id,
                'threat_score': threat_score,
                'critical_threats': critical_count,
                'total_conversations': len(conversations)
            })
        
        # Sort by threat score
        return sorted(profile_threat_scores, key=lambda x: x['threat_score'], reverse=True)[:top_n]
    
    @staticmethod
    def generate_analytics_report(profile_conversations_map: Dict[int, List[Conversation]]) -> Dict:
        """
        Generate comprehensive analytics report for all profiles.
        """
        all_conversations = []
        for conversations in profile_conversations_map.values():
            all_conversations.extend(conversations)
        
        return {
            'total_profiles': len(profile_conversations_map),
            'total_conversations': len(all_conversations),
            'top_performers': AnalyticsEngine.rank_profiles_by_success(profile_conversations_map)[:5],
            'threat_attractors': AnalyticsEngine.identify_top_threat_attractors(profile_conversations_map),
            'attack_distribution': AnalyticsEngine.get_attack_type_distribution(all_conversations),
            'severity_distribution': AnalyticsEngine.get_severity_distribution(all_conversations),
            'active_conversations': sum(1 for c in all_conversations if c.status == 'active'),
            'ended_conversations': sum(1 for c in all_conversations if c.status == 'ended'),
        }
