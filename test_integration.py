
"""
test_integration.py - Test the complete system
"""

import json
from bait_generator import BaitGenerator
from chat_engine import ChatEngine

def test_complete_flow():
    """Test the complete profile generation and chat flow."""
    print("=" * 60)
    print("TESTING COMPLETE PERSONALITY CLOAKING SYSTEM")
    print("=" * 60)

    # Initialize components
    bait_gen = BaitGenerator()
    chat_eng = ChatEngine()

    # Test traits
    test_traits = ["high_neuroticism", "high_agreeableness", "high_extraversion"]

    for trait in test_traits:
        print(f"\n{'='*40}")
        print(f"TESTING TRAIT: {trait.upper()}")
        print(f"{'='*40}")

        # 1. Generate profile
        print(f"\n1. Generating {trait} profile...")
        profile = bait_gen.generate_profile(trait)

        print(f"   Bio: {profile['bio']}")
        print(f"   Scores: {json.dumps(profile['personality_scores'], indent=12)}")

        # 2. Verify consistency
        print(f"\n2. Verifying profile consistency...")
        is_consistent = bait_gen.verify_profile_consistency(profile)
        print(f"   Consistent: {is_consistent}")

        # 3. Test chat responses
        print(f"\n3. Testing chat responses...")
        scam_messages = [
            "URGENT: Your account was hacked! Click now!",
            "Congratulations! You won a free iPhone!",
            "I need your help transferring money..."
        ]

        for i, message in enumerate(scam_messages, 1):
            response = chat_eng.generate_chat_response(
                profile["personality_scores"],
                message
            )
            print(f"\n   Scam {i}: {message}")
            print(f"   Response: {response}")

        # 4. Analyze response personality
        print(f"\n4. Analyzing response personality...")
        test_response = chat_eng.generate_chat_response(
            profile["personality_scores"],
            "Your computer has a virus!"
        )
        response_scores = chat_eng.analyze_response_personality(test_response)
        print(f"   Response: {test_response}")
        print(f"   Analyzed scores: {json.dumps(response_scores, indent=12)}")

        # Check if response matches profile
        profile_dominant = max(profile["personality_scores"],
                             key=profile["personality_scores"].get)
        response_dominant = max(response_scores, key=response_scores.get)

        print(f"   Profile dominant: {profile_dominant}")
        print(f"   Response dominant: {response_dominant}")
        print(f"   Match: {profile_dominant == response_dominant}")

def generate_training_data():
    """Generate training data for fine-tuning."""
    print("\n" + "="*60)
    print("GENERATING TRAINING DATA")
    print("="*60)

    from training_samples import TrainingDataGenerator

    generator = TrainingDataGenerator()
    dataset = generator.generate_dataset(samples_per_trait=20)  # Small for testing

    # Save dataset
    generator.save_dataset(dataset, "data/test_fine_tune_data.json")

    print(f"\nGenerated {len(dataset)} training samples")
    print("Sample:")
    print(json.dumps(dataset[0], indent=2))

if __name__ == "__main__":
    # Test the complete flow
    test_complete_flow()

    # Generate training data
    generate_training_data()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)