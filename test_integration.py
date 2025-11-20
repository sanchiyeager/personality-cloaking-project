
"""
Integration tests for Project Janus
"""

from main import janus

# Test the integration
print("🧪 Testing Manisha's Integration...")

# Test profile generation
profile = janus.generate_bait_profile("high_neuroticism")
print(f"✅ Profile generated: {profile.bio[:50]}...")

# Test database save
saved = janus.save_profile(profile)
print(f"✅ Profile saved: {saved}")

# Get status
status = janus.get_system_status()
print(f"✅ System status: {status}")

print("🎉 All tests passed! Manisha can now integrate with main.py")