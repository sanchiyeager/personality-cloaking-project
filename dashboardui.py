import streamlit as st
import plotly.graph_objects as go
import time
import random
from datetime import datetime

# -----------------------------
# IMPORT BACKEND (JANUS)
# -----------------------------
from main import janus


# -----------------------------
# BACKEND CONNECTOR
# -----------------------------
def get_bait_profile(trait):
    profile = janus.generate_bait_profile(trait)
    return profile.to_dict()


# -----------------------------
# SIMULATED AI RESPONSE
# -----------------------------
def generate_ai_reply(message, trait):
    responses = {
        "high_neuroticism": [
            "I’m not sure… this feels risky.",
            "This is making me anxious.",
            "Can you explain more?"
        ],
        "high_extraversion": [
            "Oh wow 😄 sounds interesting!",
            "Haha okay, tell me more!",
            "That’s exciting!"
        ],
        "low_openness": [
            "I don’t usually try new things.",
            "I prefer to be careful.",
            "I’m not comfortable with this."
        ],
        "low_agreeableness": [
            "Why should I trust you?",
            "This doesn’t sound right.",
            "I don’t believe this."
        ],
        "high_conscientiousness": [
            "I need proper verification.",
            "Let me check the details first.",
            "I prefer documented proof."
        ]
    }
    return random.choice(responses.get(trait, ["Okay."]))


# -----------------------------
# STREAMLIT CONFIG
# -----------------------------
st.set_page_config(page_title="Persona Cloak Command Center", layout="wide")
st.title("🛡 Persona Cloak — Command Center")
st.markdown("---")


# -----------------------------
# SESSION STATE
# -----------------------------
if "profile_data" not in st.session_state:
    st.session_state.profile_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ai_typing" not in st.session_state:
    st.session_state.ai_typing = False


# -----------------------------
# CSS (WHATSAPP STYLE)
# -----------------------------
st.markdown("""
<style>
.chat-container {
    height: 420px;
    overflow-y: auto;
    background-color: #ECE5DD;
    padding: 10px;
    border-radius: 10px;
}
.msg {
    max-width: 75%;
    padding: 10px;
    border-radius: 12px;
    margin: 6px;
    font-size: 14px;
}
.user {
    background-color: #DCF8C6;
    margin-left: auto;
    text-align: right;
}
.ai {
    background-color: white;
    margin-right: auto;
}
.time {
    font-size: 10px;
    color: gray;
}
.badge {
    background-color: #25D366;
    color: white;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 11px;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# LAYOUT
# -----------------------------
left_col, right_col = st.columns([1, 1])

# =================================================
# LEFT PANEL — PROFILE GENERATOR
# =================================================
with left_col:
    st.subheader("🎭 Bait Profile Generator")

    trait = st.selectbox(
        "Select Target Personality Trait",
        [
            "high_neuroticism",
            "low_openness",
            "high_extraversion",
            "low_agreeableness",
            "high_conscientiousness"
        ]
    )

    if st.button("✨ Generate Bait Profile"):
        with st.spinner("Generating bait profile..."):
            st.session_state.profile_data = get_bait_profile(trait)
            st.session_state.chat_history = []

    if st.session_state.profile_data:
        data = st.session_state.profile_data

        st.markdown("### 📝 Generated Bio")
        st.info(data["bio"])

        st.markdown("### 📊 Personality Scores")
        traits = data["personality"]
        st.json(traits)

        labels = list(traits.keys())
        values = list(traits.values())
        labels += labels[:1]
        values += values[:1]

        fig = go.Figure(
            data=[go.Scatterpolar(r=values, theta=labels, fill='toself')],
            layout=go.Layout(
                polar=dict(radialaxis=dict(range=[0, 1])),
                showlegend=False
            )
        )
        st.plotly_chart(fig, use_container_width=True)

# =================================================
# RIGHT PANEL — CHAT UI
# =================================================
with right_col:
    st.subheader("💬 Scam Interaction Simulator")

    if not st.session_state.profile_data:
        st.warning("Generate a bait profile to start chatting.")
    else:
        # HEADER
        st.markdown(
            f"""
            <div style="background:#075E54;color:white;padding:10px;border-radius:8px;">
            <b>Bait Profile</b>
            <span class="badge">{trait.replace("_"," ").title()}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # CHAT WINDOW
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for chat in st.session_state.chat_history:
            role = "user" if chat["sender"] == "Scammer" else "ai"
            st.markdown(
                f"""
                <div class="msg {role}">
                    {chat["text"]}
                    <div class="time">{chat["time"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.session_state.ai_typing:
            st.markdown("<i>🤖 AI is typing...</i>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # QUICK REPLIES
        st.markdown("*Quick Scam Messages*")
        quick = [
            "Your account will be blocked today!",
            "You won a lottery prize!",
            "Urgent help needed!"
        ]

        cols = st.columns(3)
        message = ""
        for col, q in zip(cols, quick):
            if col.button(q):
                message = q

        if not message:
            message = st.text_input("Type a message")

        # SEND MESSAGE
        if st.button("Send"):
            if message.strip():
                now = datetime.now().strftime("%H:%M")
                st.session_state.chat_history.append({
                    "sender": "Scammer",
                    "text": message,
                    "time": now
                })
                st.session_state.ai_typing = True
                st.experimental_rerun()

        # AI RESPONSE
        if st.session_state.ai_typing:
            time.sleep(random.randint(1, 3))
            reply = generate_ai_reply(message, trait)
            now = datetime.now().strftime("%H:%M")

            st.session_state.chat_history.append({
                "sender": "AI",
                "text": reply,
                "time": now
            })
            st.session_state.ai_typing = False
            st.experimental_rerun()

        # CONTROLS
        st.markdown("---")
        col1, col2 = st.columns(2)

        if col1.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

        if col2.button("📄 Export Chat"):
            chat_text = "\n".join(
                [f"{c['sender']}: {c['text']}" for c in st.session_state.chat_history]
            )
            st.download_button(
                "Download Conversation",
                chat_text,
                file_name="chat_history.txt"
            )
