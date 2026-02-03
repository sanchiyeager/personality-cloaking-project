import streamlit as st
import plotly.graph_objects as go
import random
import time
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide", page_title="Persona Cloak")

# -------------------------------------------------
# MOCK PERSONALITY DATA
# -------------------------------------------------
PERSONALITY = {
    "openness": 0.42,
    "conscientiousness": 0.78,
    "extraversion": 0.31,
    "agreeableness": 0.56,
    "neuroticism": 0.74
}

BIO = "I tend to be cautious online and prefer to verify information before trusting anyone."

PERSONALITY_MODE = "High Neuroticism"

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "typing" not in st.session_state:
    st.session_state.typing = False

# -------------------------------------------------
# GLOBAL STYLES
# -------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.sidebar-box {
    background-color: #111827;
    padding: 16px;
    border-radius: 12px;
    color: white;
}
.chat-header {
    background-color: #075E54;
    padding: 14px;
    color: white;
    font-size: 16px;
    border-radius: 10px 10px 0 0;
}
.chat-window {
    background-color: #ECE5DD;
    height: 500px;
    padding: 16px;
    overflow-y: auto;
}
.msg {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-size: 14px;
}
.user {
    background-color: #DCF8C6;
    margin-left: auto;
}
.ai {
    background-color: white;
    margin-right: auto;
}
.time {
    font-size: 10px;
    color: gray;
    text-align: right;
}
.input-box {
    background-color: #f0f2f5;
    padding: 10px;
    border-radius: 0 0 10px 10px;
}
.badge {
    background-color: #22c55e;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------
left, right = st.columns([1, 2])

# =================================================
# LEFT SIDEBAR — PERSONALITY PANEL
# =================================================
with left:
    st.markdown("<div class='sidebar-box'>", unsafe_allow_html=True)

    st.markdown("### 🧠 Personality Cloak")
    st.markdown(f"<span class='badge'>{PERSONALITY_MODE}</span>", unsafe_allow_html=True)

    st.markdown("#### Bio")
    st.write(BIO)

    st.markdown("#### Big Five Overview")

    # Radar Chart
    labels = list(PERSONALITY.keys())
    values = list(PERSONALITY.values())
    labels += labels[:1]
    values += values[:1]

    fig = go.Figure(
        data=[go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself"
        )],
        layout=go.Layout(
            polar=dict(radialaxis=dict(range=[0,1])),
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RIGHT PANEL — CHAT
# =================================================
with right:
    st.markdown(
        f"""
        <div class="chat-header">
            Bait Profile
            <span class="badge" style="float:right;">{PERSONALITY_MODE}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='chat-window'>", unsafe_allow_html=True)

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

    if st.session_state.typing:
        st.markdown("<i>AI is typing...</i>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Input area
    st.markdown("<div class='input-box'>", unsafe_allow_html=True)

    user_input = st.text_input("Type a message", label_visibility="collapsed")

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

    # AI response
    if st.session_state.typing:
        time.sleep(random.randint(1, 2))
        reply = random.choice([
            "I’m not sure this is safe.",
            "Can you give more details?",
            "I usually avoid these things."
        ])
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat.append({
            "sender": "AI",
            "text": reply,
            "time": now
        })
        st.session_state.typing = False
        st.experimental_rerun()
