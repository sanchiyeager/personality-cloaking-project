import streamlit as st
import plotly.graph_objects as go
import random
import time

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="Persona Cloak", layout="wide")

st.title("🛡 Persona Cloak — Command Center")

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------
# MOCK DATA (UI ONLY)
# -----------------------------------
PERSONALITY_MODE = "High Neuroticism"

PERSONALITY = {
    "Openness": 0.42,
    "Conscientiousness": 0.78,
    "Extraversion": 0.31,
    "Agreeableness": 0.56,
    "Neuroticism": 0.74
}

BIO = (
    "I prefer to stay cautious online and usually verify information "
    "before trusting unknown messages."
)

AI_REPLIES = [
    "I’m not sure this is safe.",
    "Can you explain more?",
    "This feels risky.",
    "I usually avoid such things.",
    "Please provide proper verification."
]

# -----------------------------------
# LAYOUT
# -----------------------------------
left, right = st.columns([1, 2])

# ===================================
# LEFT PANEL — PERSONALITY SIDEBAR
# ===================================
with left:
    st.subheader("🧠 Persona Profile")
    st.caption("Digital Personality Cloak")

    st.markdown(f"*Mode:* {PERSONALITY_MODE}")

    st.markdown("### Bio")
    st.write(BIO)

    st.markdown("### Big Five Traits")

    fig = go.Figure(
        data=[go.Bar(x=list(PERSONALITY.keys()), y=list(PERSONALITY.values()))]
    )
    fig.update_layout(
        height=300,
        yaxis=dict(range=[0, 1]),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===================================
# RIGHT PANEL — REAL CHAT UI
# ===================================
with right:
    st.subheader("💬 Scam Interaction Simulator")
    st.caption(f"Chatting with bait profile ({PERSONALITY_MODE})")

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box (ALWAYS at bottom)
    user_input = st.chat_input("Type a scam message...")

    if user_input:
        # User message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Simulate AI thinking
        with st.chat_message("assistant"):
            with st.spinner("AI is typing..."):
                time.sleep(random.randint(1, 2))
                reply = random.choice(AI_REPLIES)
                st.markdown(reply)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })
