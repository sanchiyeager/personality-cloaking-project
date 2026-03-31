"""
Chat Tracker Integration Examples

Demonstrates usage of:
1. Chat Tracker API endpoints
2. Analytics functions for profile success tracking
3. Conversation queue system for handling multiple conversations
"""

import time
from datetime import datetime
from core.database_module import (
    create_conversation, add_message, get_conversation, 
    get_profile_conversations, save_engagement_metrics, 
    save_attack_classification
)
from core.engagement_tracker import EngagementTracker, AnalyticsEngine
from conversation_queue import (
    ConversationManager, ConversationPriority, get_conversation_manager
)


# ==================== EXAMPLE 1: API ENDPOINT USAGE ====================

def example_1_api_integration():
    """
    Example 1: How to integrate Chat Tracker API endpoints with FastAPI
    
    This shows the basic API structure for saving and retrieving conversations.
    """
    print("\n=== EXAMPLE 1: API Endpoint Integration ===\n")
    
    print("✓ Chat Tracker API provides these endpoints:")
    print("  POST   /api/v1/conversations")
    print("  GET    /api/v1/conversations/{conversation_id}")
    print("  GET    /api/v1/profiles/{profile_id}/conversations")
    print("  POST   /api/v1/conversations/{conversation_id}/end")
    print("  POST   /api/v1/conversations/{conversation_id}/messages")
    print("  GET    /api/v1/conversations/{conversation_id}/messages")
    print("  GET    /api/v1/conversations/{conversation_id}/metrics")
    print("  POST   /api/v1/conversations/{conversation_id}/classify")
    print("  GET    /api/v1/conversations/{conversation_id}/summary")
    print("  GET    /api/v1/profiles/{profile_id}/high-risk")
    
    print("\nExample usage:")
    print("""
    import requests
    
    # Create conversation
    response = requests.post(
        'http://localhost:8000/api/v1/conversations',
        json={
            'profile_id': 1,
            'attacker_id': 'attacker_001',
            'scam_type': 'romance_scam'
        }
    )
    conv_id = response.json()['conversation_id']
    
    # Add message
    requests.post(
        f'http://localhost:8000/api/v1/conversations/{conv_id}/messages',
        json={
            'sender_type': 'attacker',
            'message_text': 'Hi there!'
        }
    )
    
    # Get conversation summary
    summary = requests.get(
        f'http://localhost:8000/api/v1/conversations/{conv_id}/summary'
    ).json()
    
    # Get high-risk conversations
    high_risk = requests.get(
        f'http://localhost:8000/api/v1/profiles/1/high-risk'
    ).json()
    """)


# ==================== EXAMPLE 2: ANALYTICS FOR PROFILE SUCCESS ====================

def example_2_profile_analytics():
    """
    Example 2: Using analytics functions to track bait profile success
    
    This demonstrates how to measure which profiles are most effective at
    attracting and engaging with attackers.
    """
    print("\n=== EXAMPLE 2: Profile Success Analytics ===\n")
    
    # Create multiple profiles with conversations
    profile_conversations = {}
    
    # Profile 1: Romance profile (aggressive engagement)
    print("Creating profile 1: Romance Bait Profile")
    conv1_id = create_conversation(profile_id=1, attacker_id="attacker_001", scam_type="romance_scam")
    add_message(conv1_id, "attacker", "Hi beautiful!")
    add_message(conv1_id, "bait_profile", "Hello! How are you?")
    add_message(conv1_id, "attacker", "I'm great! Want to chat more?")
    add_message(conv1_id, "bait_profile", "Sure, I'd love that!")
    add_message(conv1_id, "attacker", "Can you help me with something?")
    add_message(conv1_id, "bait_profile", "What do you need?")
    profile_conversations[1] = [get_conversation(conv1_id)]
    
    # Profile 2: Tech Support profile (slower engagement)
    print("Creating profile 2: Tech Support Bait Profile")
    conv2_id = create_conversation(profile_id=2, attacker_id="attacker_002", scam_type="tech_support")
    add_message(conv2_id, "attacker", "Your computer has an error")
    add_message(conv2_id, "bait_profile", "What kind of error?")
    profile_conversations[2] = [get_conversation(conv2_id)]
    
    # Calculate success metrics for each profile
    print("\nProfile Success Metrics:")
    for profile_id, conversations in profile_conversations.items():
        metrics = AnalyticsEngine.calculate_profile_success_metrics(conversations)
        
        print(f"\nProfile {profile_id}:")
        print(f"  Total Conversations: {metrics['total_conversations']}")
        print(f"  Active: {metrics['active_conversations']}, Ended: {metrics['ended_conversations']}")
        print(f"  Success Rate: {metrics['success_rate']:.2%}")
        print(f"  Avg Conversation Length: {metrics['avg_conversation_length']:.1f} messages")
        print(f"  Avg Response Time: {metrics['avg_response_time']:.1f}s" if metrics['avg_response_time'] else "  Avg Response Time: N/A")
        print(f"  Threat Capture Score: {metrics['threat_capture_score']:.2f}")
    
    # Rank profiles by success
    print("\n\nProfile Rankings by Success:")
    rankings = AnalyticsEngine.rank_profiles_by_success(profile_conversations)
    for i, ranking in enumerate(rankings, 1):
        print(f"{i}. Profile {ranking['profile_id']}: Score {ranking['composite_score']:.3f}")
    
    # Effectiveness analysis
    print("\n\nProfile Effectiveness Analysis:")
    for profile_id, conversations in profile_conversations.items():
        effectiveness = AnalyticsEngine.calculate_bait_effectiveness(profile_id, conversations)
        
        print(f"\nProfile {profile_id} Effectiveness: {effectiveness['effectiveness']:.2%}")
        print(f"  Engagement Rate: {effectiveness['engagement_rate']:.2%}")
        print(f"  Attack Diversity: {effectiveness['attack_diversity']} types")
        print(f"  Avg Conversation Duration: {effectiveness['avg_conversation_duration']:.0f}s")
        print(f"  Avg Sentiment: {effectiveness['avg_sentiment']:.2f}")


# ==================== EXAMPLE 3: QUEUE SYSTEM ====================

def example_3_queue_system():
    """
    Example 3: Using the conversation queue system to handle multiple conversations
    
    This demonstrates how to efficiently manage many conversations with
    priority queuing and rate limiting.
    """
    print("\n=== EXAMPLE 3: Conversation Queue System ===\n")
    
    # Get the global conversation manager
    manager = get_conversation_manager()
    
    print("✓ Conversation Manager initialized")
    print(f"  Queue workers: {manager.queue.workers}")
    print(f"  Rate limits: {manager.rate_limiter.max_messages}/min messages, {manager.rate_limiter.max_conversations}/min conversations")
    
    # Create multiple conversations
    print("\nCreating 5 conversations...")
    conversations = []
    for i in range(5):
        conv_id = create_conversation(
            profile_id=1,
            attacker_id=f"attacker_{i:03d}",
            scam_type="financial_fraud"
        )
        conversations.append(conv_id)
        print(f"  Created conversation {conv_id}")
    
    # Queue messages with different priorities
    print("\nQueuing messages with priorities...")
    
    # Normal priority messages
    for i, conv_id in enumerate(conversations[:3]):
        success = manager.add_message(
            conversation_id=conv_id,
            attacker_id=f"attacker_{i:03d}",
            sender_type="attacker",
            message=f"Investment opportunity message {i}",
            priority=ConversationPriority.NORMAL
        )
        print(f"  Conversation {conv_id}: Queued (Normal) - {'✓' if success else '✗'}")
    
    # High priority messages (high-risk attacks)
    for i in range(3, 5):
        success = manager.add_message(
            conversation_id=conversations[i],
            attacker_id=f"attacker_{i:03d}",
            sender_type="attacker",
            message=f"Critical threat message {i}",
            priority=ConversationPriority.HIGH
        )
        print(f"  Conversation {conversations[i]}: Queued (High Priority) - {'✓' if success else '✗'}")
    
    # Check queue status
    print("\nQueue Status:")
    status = manager.get_status()
    print(f"  Queue size: {status['queue']['queue_size']}")
    print(f"  Processed: {status['queue']['processed']}")
    print(f"  Failed: {status['queue']['failed']}")
    print(f"  Workers: {status['queue']['workers']}")
    
    # Rate limiter status
    print("\nRate Limiter Status:")
    rl_status = status['rate_limiter']
    print(f"  Messages this minute: {rl_status['messages_this_minute']}/{rl_status['max_messages_per_minute']}")
    print(f"  Conversations this minute: {rl_status['conversations_this_minute']}/{rl_status['max_conversations_per_minute']}")
    print(f"  Capacity available: {rl_status['message_capacity_available']} messages, {rl_status['conversation_capacity_available']} conversations")


# ==================== EXAMPLE 4: COMPLETE WORKFLOW ====================

def example_4_complete_workflow():
    """
    Example 4: Complete workflow using API, Analytics, and Queue together
    
    This demonstrates a realistic scenario where:
    1. Multiple conversations are created via API
    2. Messages are queued for processing
    3. Analytics track profile performance
    4. High-risk conversations are identified
    """
    print("\n=== EXAMPLE 4: Complete Integrated Workflow ===\n")
    
    manager = get_conversation_manager()
    
    print("Step 1: Creating bait profiles and initiating conversations")
    print("-" * 50)
    
    # Create 3 bait profiles
    profiles = []
    for i in range(1, 4):
        profiles.append({
            'profile_id': i,
            'name': f'Profile_{i}',
            'conversations': []
        })
        print(f"  Created Profile {i}")
    
    print("\nStep 2: Simulating attacker engagement")
    print("-" * 50)
    
    # Simulate conversations
    conversation_count = 0
    for profile_idx, profile in enumerate(profiles):
        for attacker_idx in range(3):  # 3 attackers per profile
            conv_id = create_conversation(
                profile_id=profile['profile_id'],
                attacker_id=f"attacker_{profile_idx}_{attacker_idx}",
                scam_type="romance_scam" if profile_idx == 0 else "phishing" if profile_idx == 1 else "financial_fraud"
            )
            profile['conversations'].append(conv_id)
            conversation_count += 1
    
    print(f"  Created {conversation_count} conversations across {len(profiles)} profiles")
    
    print("\nStep 3: Queuing messages for processing")
    print("-" * 50)
    
    # Queue messages
    messages_queued = 0
    for profile_idx, profile in enumerate(profiles):
        for conv_idx, conv_id in enumerate(profile['conversations']):
            # Attacker message
            priority = ConversationPriority.CRITICAL if profile_idx == 0 else ConversationPriority.NORMAL
            manager.add_message(
                conversation_id=conv_id,
                attacker_id=f"attacker_{profile_idx}_{conv_idx}",
                sender_type="attacker",
                message=f"Test message from attacker {profile_idx}_{conv_idx}",
                priority=priority
            )
            messages_queued += 1
            
            # Bait response
            manager.add_message(
                conversation_id=conv_id,
                attacker_id=f"attacker_{profile_idx}_{conv_idx}",
                sender_type="bait_profile",
                message=f"Response from profile {profile_idx}",
                priority=ConversationPriority.NORMAL
            )
            messages_queued += 1
    
    print(f"  Queued {messages_queued} messages for processing")
    
    print("\nStep 4: Analyzing profile performance")
    print("-" * 50)
    
    # Wait a bit for queue to process
    time.sleep(2)
    
    # Collect conversations for analytics
    profile_conversations_map = {}
    for profile in profiles:
        profile_conversations_map[profile['profile_id']] = [
            get_conversation(conv_id) for conv_id in profile['conversations']
        ]
    
    # Generate analytics report
    report = AnalyticsEngine.generate_analytics_report(profile_conversations_map)
    
    print(f"  Total Profiles: {report['total_profiles']}")
    print(f"  Total Conversations: {report['total_conversations']}")
    print(f"  Active Conversations: {report['active_conversations']}")
    print(f"  Ended Conversations: {report['ended_conversations']}")
    
    print("\n  Top Performing Profiles:")
    for ranking in report['top_performers'][:3]:
        print(f"    Profile {ranking['profile_id']}: Score {ranking['composite_score']:.3f}")
        print(f"      Success Rate: {ranking['metrics']['success_rate']:.2%}")
        print(f"      Threat Capture: {ranking['metrics']['threat_capture_score']:.2f}")
    
    print("\n  Threat Attractors:")
    for threat in report['threat_attractors'][:3]:
        print(f"    Profile {threat['profile_id']}: Threat Score {threat['threat_score']:.2f}")
        print(f"      Critical Threats: {threat['critical_threats']}")
    
    print("\n  Attack Distribution:")
    for attack_type, count in report['attack_distribution'].items():
        if count > 0:
            print(f"    {attack_type}: {count}")


# ==================== EXAMPLE 5: MONITORING & ADMINISTRATION ====================

def example_5_monitoring():
    """
    Example 5: Monitoring queue health and managing failed tasks
    """
    print("\n=== EXAMPLE 5: Queue Monitoring & Administration ===\n")
    
    manager = get_conversation_manager()
    
    print("Getting queue status...")
    status = manager.get_status()
    
    print(f"\nQueue Statistics:")
    print(f"  Running: {status['queue']['running']}")
    print(f"  Queue Size: {status['queue']['queue_size']}")
    print(f"  Workers: {status['queue']['workers']}")
    print(f"  Processed: {status['queue']['processed']}")
    print(f"  Failed: {status['queue']['failed']}")
    print(f"  Retried: {status['queue']['retried']}")
    print(f"  Failed Tasks: {status['queue']['failed_tasks']}")
    
    print(f"\nRate Limiter Status:")
    rl = status['rate_limiter']
    print(f"  Messages: {rl['messages_this_minute']}/{rl['max_messages_per_minute']} used")
    print(f"  Conversations: {rl['conversations_this_minute']}/{rl['max_conversations_per_minute']} used")
    
    print(f"\nBatcher Status:")
    print(f"  Batch Size: {status['batcher']['batch_size']}")
    print(f"  Current Batch: {status['batcher']['current_batch_size']}")
    print(f"  Processed Batches: {status['batcher']['processed_batches']}")
    
    # Get failed tasks
    if status['queue']['failed_tasks'] > 0:
        print(f"\nFailed Tasks:")
        failed = manager.queue.get_failed_tasks()
        for task in failed[:5]:
            print(f"  Conv {task['conversation_id']}: {task['retry_count']} retries")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("CHAT TRACKER INTEGRATION - COMPREHENSIVE EXAMPLES")
    print("=" * 60)
    
    try:
        example_1_api_integration()
        example_2_profile_analytics()
        example_3_queue_system()
        example_4_complete_workflow()
        example_5_monitoring()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
