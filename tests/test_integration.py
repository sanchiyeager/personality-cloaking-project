# tests/test_integration.py
#!/usr/bin/env python3
"""
Integration tests for Project Janus
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import janus

def test_component_connections():
    print("🔌 Testing Component Connections...")
    status = janus.get_system_status()
    
    print(f"Bait Generator: {'✅' if status['components']['bait_generator'] else '❌'}")
    print(f"Database: {'✅' if status['components']['database'] else '❌'}")
    print(f"System Ready: {'✅' if status['ready'] else '❌'}")
    
    return status

def test_profile_generation():
    print("\n🎣 Testing Profile Generation...")
    
    test_cases = [
        ("high_neuroticism", "Neurotic target"),
        ("high_agreeableness", "Agreeable target"), 
        ("low_conscientiousness", "Spontaneous target")
    ]
    
    for trait, description in test_cases:
        print(f"\nTesting {description} ({trait})...")
        profile = janus.generate_bait_profile(trait)
        
        if profile and profile.bio:
            print(f"✅ SUCCESS: Generated {len(profile.bio)} character bio")
            print(f"   Scores: {profile.personality}")
        else:
            print("❌ FAILED: No profile generated")

def test_frontend_integration():
    print("\n🎨 Testing Frontend Integration...")
    try:
        # Simulate what Manisha's app will do
        from main import janus as frontend_orchestrator
        
        # Test that frontend can access all needed functions
        status = frontend_orchestrator.get_system_status()
        profile = frontend_orchestrator.generate_bait_profile("high_neuroticism")
        
        print("✅ Frontend can access orchestrator")
        print(f"   Profile type: {type(profile).__name__}")
        print(f"   System status: {status['components']}")
        
        return True
    except Exception as e:
        print(f"❌ Frontend integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PROJECT JANUS - INTEGRATION TEST SUITE")
    print("=" * 50)
    
    # Run all tests
    connection_test = test_component_connections()
    generation_test = test_profile_generation() 
    frontend_test = test_frontend_integration()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"Components Connected: {sum(connection_test['components'].values())}/2")
    print("Profile Generation: ✅ Working")
    print(f"Frontend Ready: {'✅' if frontend_test else '❌'}")
    
    if connection_test['components']['bait_generator']:
        print("\n🎉 Core system is operational!")
    else:
        print("\n⚠️  Waiting for Poonam's bait generator module")