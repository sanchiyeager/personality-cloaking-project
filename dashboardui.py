import streamlit as st
import plotly.graph_objects as go
import time
import random
from datetime import datetime

# -----------------------------
# STREAMLIT CONFIG
# -----------------------------
st.set_page_config(page_title="Persona Cloak Command Center", layout="wide")
st.title("🛡 Persona Cloak — Command Center")
st.markdown("---")


# -----------------------------
# MOCK DATA (UI ONLY)
# -----------------------------
def get_mock_bait_profile(trait):
    return {
        "bio": "I prefer to stay cautious online and think carefully before responding.",
        "personality": {
            "openness": round(random.uniform(0.3, 0.6), 2),
            "conscientiousness": round(random.uniform(0.6, 0.9), 2),
            "extraversion": round(random.uniform(0.2, 0.5), 2),
            "agreeableness": round(random.uniform(0.4, 0.7), 2),
            "neuroticism": round(random.uniform(0.6, 0.85), 2),
        }
    }


def generate_mock_ai_reply(trait):
    replies = {
        "high_neuroticism": [
            "I’m not sure about this… it feels risky.",
            "This is making me anxious.",
            "Can you explain more?"
        ],
        "high_extraversion": [
            "Oh wow 😄 that sounds interesting!",
            "Haha okay, tell me more!",
            "That’s exciting!"
        ],
        "low_openness": [
            "I don’t usually try new things.",
            "I prefer familiar options.",
            "I’m not comfortable with this."
        ],
        "low_agreeableness": [
            "Why should I trust this?",
            "This doesn’t sound right.",
            "I don’t believe this."
        ],
        "high_conscientiousness": [
            "I need proper verification.",
            "Please provide official details.",
            "I prefer documented proof."
        ]
    }
    return random.choice(replies.get(trait, ["Okay."]))


# -----------------------------
# SESSION STATE
# -----------------------------
if "profile" not in st.session_state:
    st.session_state.profile = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "ai_typing" not in st.session_state:
    st.session_state.ai_typing = False


# -----------------------------
# CSS (WHATSAPP STYLE)
# -----------------------------
st.markdown("""
<style>
.chat-box {
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
# LEFT PANEL — PROFILE GENERATION
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
        st.session_state.profile = get_mock_bait_profile(trait)
        st.session_state.chat = []

    if st.session_state.profile:
        st.markdown("### 📝 Generated Bio")
        st.info(st.session_state.profile["bio"])

        st.markdown("### 📊 Personality Scores")
        traits = st.session_state.profile["personality"]
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

    if not st.session_state.profile:
        st.warning("Generate a bait profile to start chatting.")
    else:
        st.markdown(
            f"""
            <div style="background:#075E54;color:white;padding:10px;border-radius:8px;">
            <b>Bait Profile</b>
            <span class="badge">{trait.replace("_"," ").title()}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="chat-box">', unsafe_allow_html=True)

        for msg in st.session_state.chat:
            role = "user" if msg["sender"] == "Scammer" else "ai"
            st.markdown(
                f"""
                <div class="msg {role}">
                    {msg["text"]}
                    <div class="time">{msg["time"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.session_state.ai_typing:
            st.markdown("<i>🤖 AI is typing...</i>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("*Quick Scam Messages*")
        quick_msgs = [
            "Your account will be blocked today!",
            "You won a lottery prize!",
            "Urgent help needed!"
        ]

        cols = st.columns(3)
        user_message = ""
        for col, q in zip(cols, quick_msgs):
            if col.button(q):
                user_message = q

        if not user_message:
            user_message = st.text_input("Type a message")

        if st.button("Send"):
            if user_message.strip():
                now = datetime.now().strftime("%H:%M")
                st.session_state.chat.append({
                    "sender": "Scammer",
                    "text": user_message,
                    "time": now
                })
                st.session_state.ai_typing = True
                st.experimental_rerun()

        if st.session_state.ai_typing:
            time.sleep(random.randint(1, 3))
            reply = generate_mock_ai_reply(trait)
            now = datetime.now().strftime("%H:%M")
            st.session_state.chat.append({
                "sender": "AI",
                "text": reply,
                "time": now
            })
            st.session_state.ai_typing = False
            st.experimental_rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)

        if col1.button("🧹 Clear Chat"):
            st.session_state.chat = []
            st.experimental_rerun()

        if col2.button("📄 Export Chat"):
            chat_text = "\n".join(
                [f"{c['sender']}: {c['text']}" for c in st.session_state.chat]
            )
            st.download_button(
                "Download Conversation",
                chat_text,
                file_name="chat_history.txt"
            )
