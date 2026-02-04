import streamlit as st
import plotly.graph_objects as go
import time
import random
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Persona Cloak", layout="wide")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "typing" not in st.session_state:
    st.session_state.typing = False

# --------------------------------------------------
# MOCK DATA
# --------------------------------------------------
PERSONALITY = {
    "Openness": 0.42,
    "Conscientiousness": 0.78,
    "Extraversion": 0.31,
    "Agreeableness": 0.56,
    "Neuroticism": 0.74
}

PERSONALITY_MODE = "High Neuroticism"

# --------------------------------------------------
# CSS (TELEGRAM DARK STYLE)
# --------------------------------------------------
st.markdown("""
<style>
body { background-color:#0f172a; }
.sidebar { background:#020617; padding:15px; border-radius:12px; }
.chat-header { background:#1f2937; padding:15px; border-radius:12px 12px 0 0; }
.chat-box { background:#111827; height:480px; padding:15px; overflow-y:auto; }
.msg { padding:10px 14px; border-radius:14px; margin:8px 0; max-width:70%; }
.user { background:#2563eb; margin-left:auto; color:white; }
.ai { background:#1f2937; margin-right:auto; color:white; }
.time { font-size:10px; opacity:0.6; text-align:right; }
.input-box { background:#020617; padding:10px; border-radius:0 0 12px 12px; }
.badge { background:#22c55e; padding:4px 10px; border-radius:999px; font-size:12px; }
.analytics { background:#020617; padding:10px; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
left, right = st.columns([1, 2])

# ==================================================
# LEFT SIDEBAR — PERSONALITY PANEL
# ==================================================
with left:
    st.markdown("<div class='sidebar'>", unsafe_allow_html=True)

    st.markdown("### 🧠 Persona Cloak")
    st.markdown(f"<span class='badge'>{PERSONALITY_MODE}</span>", unsafe_allow_html=True)

    st.markdown("#### Bio")
    st.write(
        "I tend to be cautious online and verify information before responding to unknown messages."
    )

    st.markdown("#### Big Five Traits")

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(PERSONALITY.keys()),
                y=list(PERSONALITY.values())
            )
        ]
    )
    fig.update_layout(
        height=260,
        yaxis=dict(range=[0, 1]),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# RIGHT PANEL — CHAT
# ==================================================
with right:
    st.markdown(
        f"""
        <div class='chat-header'>
            <b>Bait Profile</b>
            <span class='badge' style='float:right'>{PERSONALITY_MODE}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

    for msg in st.session_state.chat:
        role = "user" if msg["sender"] == "Scammer" else "ai"
        st.markdown(
            f"""
            <div class='msg {role}'>
                {msg["text"]}
                <div class='time'>{msg["time"]} · 😊 😐 😡</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.typing:
        st.markdown("<i>🤖 AI is typing...</i>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # INPUT
    st.markdown("<div class='input-box'>", unsafe_allow_html=True)
    user_input = st.text_input("Message", placeholder="Type a message", label_visibility="collapsed")

    if st.button("Send"):
        if user_input.strip():
            now = datetime.now().strftime("%H:%M")
            st.session_state.chat.append({
                "sender": "Scammer",
                "text": user_input,
                "time": now
            })
            st.session_state.typing = True
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # AI RESPONSE
    if st.session_state.typing:
        time.sleep(random.randint(1, 2))
        reply = random.choice([
            "I’m not comfortable with this.",
            "This feels risky to me.",
            "Can you explain further?",
            "I prefer not to proceed."
        ])
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat.append({
            "sender": "AI",
            "text": reply,
            "time": now
        })
        st.session_state.typing = False
        st.experimental_rerun()

    # ANALYTICS
    st.markdown("<div class='analytics'>", unsafe_allow_html=True)
    st.markdown("### 📊 Conversation Analytics")
    st.write(f"Total Messages: {len(st.session_state.chat)}")
    st.write("Detected Sentiment: ⚠️ Cautious")
    st.markdown("</div>", unsafe_allow_html=True)
