"""
Chat History & Engagement Tracker - Usage Examples

This module demonstrates how to use the new chat tracking system:
1. Create conversations between profiles and attackers
2. Add messages to conversations
3. Calculate engagement metrics
4. Classify attacks
5. Analyze conversation patterns
"""

from datetime import datetime, timedelta
from core.models import (
    BaitProfile, Conversation, ChatMessage, 
    EngagementMetric, AttackClassification
)
from core.database_module import (
    create_conversation, add_message, end_conversation,
    get_conversation, get_profile_conversations,
    get_conversation_messages, save_engagement_metrics,
    get_engagement_metrics, save_attack_classification,
    get_attack_classifications, get_latest_attack_classification
)
from core.engagement_tracker import EngagementTracker, ConversationAnalyzer


def example_1_create_and_track_conversation():
    """Example: Create a conversation and track messages"""
    print("\n=== EXAMPLE 1: Create and Track Conversation ===\n")
    
    # Create a new conversation
    profile_id = 1
    attacker_id = "attacker_001"
    scam_type = "romance_scam"
    
    conversation_id = create_conversation(profile_id, attacker_id, scam_type)
    print(f"Created conversation: {conversation_id}")
    
    # Simulate conversation with realistic timing
    messages_data = [
        ("attacker", "Hi there! I think you're really interesting. 😊", 0),
        ("bait_profile", "Thanks! How did you find me?", 120),
        ("attacker", "I saw your profile and couldn't resist saying hello. I'm traveling for work but would love to get to know you.", 60),
        ("bait_profile", "That's sweet of you to say! What kind of work do you do?", 180),
        ("attacker", "I work in oil and gas. It's demanding but pays well. I'd love to take you out when I'm back in town.", 90),
        ("bait_profile", "That sounds interesting! When would you be back?", 150),
    ]
    
    # Add messages
    current_time = datetime.now()
    for sender, text, delay_seconds in messages_data:
        add_message(conversation_id, sender, text)
        current_time += timedelta(seconds=delay_seconds)
    
    print(f"Added {len(messages_data)} messages to conversation")
    
    # Retrieve conversation
    conversation = get_conversation(conversation_id)
    print(f"Conversation retrieved with {len(conversation.messages)} messages")
    
    return conversation_id


def example_2_calculate_engagement_metrics():
    """Example: Calculate engagement metrics"""
    print("\n=== EXAMPLE 2: Calculate Engagement Metrics ===\n")
    
    # Use the conversation from example 1
    conversation_id = example_1_create_and_track_conversation()
    
    # Get the conversation
    conversation = get_conversation(conversation_id)
    
    # Generate metrics
    metrics = EngagementTracker.generate_engagement_metrics(conversation)
    
    print(f"Engagement Metrics for Conversation {conversation_id}:")
    print(f"  Message Count: {metrics.message_count}")
    print(f"  Avg Response Time: {metrics.response_time_avg:.2f} seconds" if metrics.response_time_avg else "  Avg Response Time: N/A")
    print(f"  Min Response Time: {metrics.response_time_min:.2f} seconds" if metrics.response_time_min else "  Min Response Time: N/A")
    print(f"  Max Response Time: {metrics.response_time_max:.2f} seconds" if metrics.response_time_max else "  Max Response Time: N/A")
    print(f"  Avg Message Length: {metrics.message_length_avg:.2f} characters")
    print(f"  Total Text Length: {metrics.message_length_total} characters")
    print(f"  Sentiment Score: {metrics.sentiment_avg:.2f}")
    
    # Save metrics to database
    save_engagement_metrics(metrics)
    print(f"\n✓ Metrics saved to database")
    
    # Retrieve metrics from database
    retrieved_metrics = get_engagement_metrics(conversation_id)
    print(f"✓ Retrieved metrics from database")
    
    return conversation_id


def example_3_classify_attacks():
    """Example: Classify attack types"""
    print("\n=== EXAMPLE 3: Classify Attacks ===\n")
    
    conversation_id = example_2_calculate_engagement_metrics()
    conversation = get_conversation(conversation_id)
    
    # Classify the attack
    classification = EngagementTracker.classify_conversation_attack(conversation)
    
    print(f"Attack Classification for Conversation {conversation_id}:")
    print(f"  Attack Type: {classification.attack_type}")
    print(f"  Confidence: {classification.confidence:.2%}")
    print(f"  Severity Level: {classification.severity_level}")
    print(f"  Techniques Detected: {', '.join(classification.techniques_detected)}")
    
    # Save classification
    save_attack_classification(classification)
    print(f"\n✓ Classification saved to database")
    
    # Retrieve classifications
    classifications = get_attack_classifications(conversation_id)
    print(f"✓ Retrieved {len(classifications)} classification(s) from database")
    
    return conversation_id


def example_4_conversation_summary():
    """Example: Generate comprehensive conversation summary"""
    print("\n=== EXAMPLE 4: Conversation Summary ===\n")
    
    conversation_id = example_3_classify_attacks()
    conversation = get_conversation(conversation_id)
    
    # Generate summary
    summary = ConversationAnalyzer.get_conversation_summary(conversation)
    
    print(f"Conversation Summary (ID: {summary['conversation_id']}):")
    print(f"  Profile ID: {summary['profile_id']}")
    print(f"  Attacker ID: {summary['attacker_id']}")
    print(f"  Message Count: {summary['message_count']}")
    
    print(f"\nEngagement Metrics:")
    for key, value in summary['engagement'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nAttack Analysis:")
    for key, value in summary['attack_analysis'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        elif isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    return conversation_id


def example_5_multiple_conversations():
    """Example: Track multiple conversations and identify patterns"""
    print("\n=== EXAMPLE 5: Multiple Conversations & Pattern Analysis ===\n")
    
    profile_id = 1
    conversations = []
    
    # Create multiple different scam attempts
    scam_scenarios = [
        ("attacker_001", "romance_scam", [
            ("attacker", "I think you're amazing. Can we video call?"),
            ("bait_profile", "Sure, I'd like that!"),
            ("attacker", "Actually, I'm stuck out of the country. Can you help me with urgent funds?"),
            ("bait_profile", "I don't feel comfortable with that"),
        ]),
        ("attacker_002", "phishing", [
            ("attacker", "Click here to verify your account: bit.ly/verify"),
            ("bait_profile", "That looks suspicious"),
            ("attacker", "Your account has been compromised. Click to confirm identity"),
            ("bait_profile", "I'll verify through the official website"),
        ]),
        ("attacker_003", "financial_fraud", [
            ("attacker", "Invest $500 for 50% monthly returns"),
            ("bait_profile", "How does this work?"),
            ("attacker", "Wire transfer to my account and you'll see results"),
            ("bait_profile", "Can you send documentation?"),
        ]),
    ]
    
    for attacker_id, scam_type, messages_data in scam_scenarios:
        conv_id = create_conversation(profile_id, attacker_id, scam_type)
        
        for sender, text in messages_data:
            add_message(conv_id, sender, text)
        
        conversation = get_conversation(conv_id)
        conversations.append(conversation)
        print(f"✓ Created {scam_type} conversation (ID: {conv_id})")
    
    # Analyze all conversations
    print(f"\nAnalyzing {len(conversations)} conversations...")
    high_risk = ConversationAnalyzer.identify_high_risk_conversations(conversations)
    
    print(f"\nHigh-Risk Conversations Found: {len(high_risk)}")
    for risk in high_risk:
        print(f"\n  Conversation ID: {risk['conversation_id']}")
        print(f"    Attack Type: {risk['attack_type']}")
        print(f"    Severity: {risk['severity']}")
        print(f"    Confidence: {risk['confidence']:.2%}")
        print(f"    Techniques: {', '.join(risk['techniques'])}")


def example_6_end_conversation():
    """Example: End conversation and finalize metrics"""
    print("\n=== EXAMPLE 6: End Conversation ===\n")
    
    conversation_id = example_4_conversation_summary()
    
    # End the conversation
    success = end_conversation(conversation_id)
    if success:
        print(f"✓ Conversation {conversation_id} marked as ended")
    
    # Verify
    conversation = get_conversation(conversation_id)
    print(f"  Status: {conversation.status}")
    if conversation.ended_at:
        duration = (conversation.ended_at - conversation.started_at).total_seconds()
        print(f"  Duration: {duration:.0f} seconds")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("CHAT HISTORY & ENGAGEMENT TRACKER - EXAMPLES")
    print("=" * 60)
    
    try:
        example_1_create_and_track_conversation()
        example_2_calculate_engagement_metrics()
        example_3_classify_attacks()
        example_4_conversation_summary()
        example_5_multiple_conversations()
        example_6_end_conversation()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
