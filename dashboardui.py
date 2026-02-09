import streamlit as st
import plotly.graph_objects as go
import random
import time
from datetime import datetime

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Persona Cloak",
    layout="wide"
)

st.title("🛡 Persona Cloak — Command Center")
st.markdown("---")

# ==================================================
# SESSION STATE
# ==================================================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "typing" not in st.session_state:
    st.session_state.typing = False

# ==================================================
# MOCK DATA (UI ONLY)
# ==================================================
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
    "before responding to unknown messages."
)

AI_REPLIES = [
    "I’m not sure this is safe.",
    "Can you explain more?",
    "This feels risky to me.",
    "I usually avoid such things.",
    "Please provide official details."
]

# ==================================================
# CSS (WHATSAPP / TELEGRAM DESKTOP STYLE)
# ==================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
}

/* LEFT SIDEBAR */
.left-panel {
    background-color: #020617;
    padding: 18px;
    border-radius: 14px;
}

/* CHAT HEADER */
.chat-header {
    background-color: #075E54;
    color: white;
    padding: 14px;
    border-radius: 14px 14px 0 0;
    font-size: 16px;
    font-weight: 600;
}

/* CHAT BOX */
.chat-box {
    background-color: #ECE5DD;
    height: 480px;
    padding: 14px;
    overflow-y: auto;
}

/* MESSAGE BUBBLES */
.msg {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 14px;
    margin-bottom: 10px;
    font-size: 14px;
    line-height: 1.4;
}

.user {
    background-color: #DCF8C6;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.ai {
    background-color: white;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

/* TIMESTAMP */
.time {
    font-size: 10px;
    color: gray;
    text-align: right;
    margin-top: 2px;
}

/* INPUT BAR */
.input-bar {
    background-color: #f0f2f5;
    padding: 10px;
    border-radius: 0 0 14px 14px;
}

/* BADGE */
.badge {
    background-color: #25D366;
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# LAYOUT
# ==================================================
left_col, right_col = st.columns([1, 2])

# ==================================================
# LEFT PANEL — PERSONALITY SIDEBAR
# ==================================================
with left_col:
    st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

    st.markdown("### 🧠 Persona Profile")
    st.markdown(f"<span class='badge'>{PERSONALITY_MODE}</span>", unsafe_allow_html=True)

    st.markdown("#### Bio")
    st.write(BIO)

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
        height=280,
        yaxis=dict(range=[0, 1]),
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# RIGHT PANEL — CHAT INTERFACE
# ==================================================
with right_col:
    st.markdown(
        f"""
        <div class="chat-header">
            Bait Profile
            <span class="badge">{PERSONALITY_MODE}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

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
        st.markdown("<i>🤖 AI is typing...</i>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # INPUT BAR
    st.markdown("<div class='input-bar'>", unsafe_allow_html=True)

    user_input = st.text_input(
        "Message",
        placeholder="Type a message",
        label_visibility="collapsed"
    )

    send = st.button("Send")

    st.markdown("</div>", unsafe_allow_html=True)

    # HANDLE MESSAGE SEND
    if send and user_input.strip():
        now = datetime.now().strftime("%H:%M")

        st.session_state.chat.append({
            "sender": "Scammer",
            "text": user_input,
            "time": now
        })

        st.session_state.typing = True
        st.experimental_rerun()

    # AI RESPONSE
    if st.session_state.typing:
        time.sleep(random.randint(1, 2))
        reply = random.choice(AI_REPLIES)
        now = datetime.now().strftime("%H:%M")

        st.session_state.chat.append({
            "sender": "AI",
            "text": reply,
            "time": now
        })

        st.session_state.typing = False
        st.experimental_rerun()
