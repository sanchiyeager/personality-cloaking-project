import streamlit as st
import plotly.graph_objects as go

# -----------------------------
# IMPORT backend (Janus Engine)
# -----------------------------
from main import janus   # backend ML system


# -----------------------------
# Backend Connector
# -----------------------------
def get_bait_profile(trait="high_neuroticism"):
    profile = janus.generate_bait_profile(trait)
    return profile.to_dict()


# -----------------------------
# Simulated AI Chat Response
# -----------------------------
def generate_ai_reply(message, trait):
    if trait == "high_neuroticism":
        return "I’m not sure… this sounds a bit risky. Can you explain more?"
    elif trait == "high_extraversion":
        return "Oh wow 😄 That sounds interesting! Tell me more!"
    elif trait == "low_openness":
        return "I usually don’t try new things. I need more details."
    elif trait == "low_agreeableness":
        return "Why should I trust this? This doesn’t make sense."
    elif trait == "high_conscientiousness":
        return "Before proceeding, I need proper verification."
    else:
        return "Okay."


# -----------------------------
# STREAMLIT CONFIG
# -----------------------------
st.set_page_config(
    page_title="Persona Cloak Command Center",
    layout="wide"
)

st.title("🛡 Persona Cloak — Command Center")

st.markdown("---")

# -----------------------------
# SESSION STATE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "profile_data" not in st.session_state:
    st.session_state.profile_data = None


# -----------------------------
# LAYOUT: DUAL PANEL
# -----------------------------
left_col, right_col = st.columns([1, 1])

# ======================================================
# LEFT PANEL — PROFILE GENERATION
# ======================================================
with left_col:
    st.subheader("🎭 Bait Profile Generator")

    trait = st.selectbox(
        "Select Target Personality Trait:",
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
            st.session_state.chat_history = []  # reset chat

    if st.session_state.profile_data:
        data = st.session_state.profile_data

        st.markdown("### 📝 Generated Bio")
        st.info(data["bio"])

        st.markdown("### 📊 Personality Scores")
        traits = data["personality"]
        st.json(traits)

        st.markdown("### 📈 Radar Chart")

        labels = list(traits.keys())
        values = list(traits.values())

        labels += labels[:1]
        values += values[:1]

        fig = go.Figure(
            data=[
                go.Scatterpolar(
                    r=values,
                    theta=[l.capitalize() for l in labels],
                    fill='toself'
                )
            ],
            layout=go.Layout(
                polar=dict(radialaxis=dict(range=[0, 1], visible=True)),
                showlegend=False
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Generate a bait profile to activate chat simulation.")

# ======================================================
# RIGHT PANEL — CHAT INTERFACE
# ======================================================
with right_col:
    st.subheader("💬 Scam Interaction Simulator")

    if not st.session_state.profile_data:
        st.warning("Please generate a bait profile first.")
    else:
        # Scam templates
        scam_templates = {
            "Lottery Scam": "Congratulations! You have won a prize. Click the link to claim.",
            "Urgent Help Scam": "I need money urgently. Please help me.",
            "Account Alert": "Your bank account will be suspended today."
        }

        template_choice = st.selectbox(
            "🎣 Scam Message Templates",
            list(scam_templates.keys())
        )

        if st.button("Use Template"):
            user_message = scam_templates[template_choice]
        else:
            user_message = ""

        message = st.text_input("Type a message:", value=user_message)
        send = st.button("Send Message")

        # Send message
        if send and message:
            st.session_state.chat_history.append({
                "sender": "Scammer",
                "text": message
            })

            ai_reply = generate_ai_reply(message, trait)

            st.session_state.chat_history.append({
                "sender": "Bait Profile",
                "text": ai_reply
            })

        st.markdown("---")

        # Chat UI
        st.markdown("### 🗨 Conversation")

        for chat in st.session_state.chat_history:
            if chat["sender"] == "Scammer":
                st.markdown(
                    f"""
                    <div style='text-align:right;
                                background:#DCF8C6;
                                padding:10px;
                                border-radius:10px;
                                margin:5px'>
                        <b>Scammer</b><br>
                        {chat["text"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='text-align:left;
                                background:#F1F0F0;
                                padding:10px;
                                border-radius:10px;
                                margin:5px'>
                        <b>Bait Profile</b><br>
                        {chat["text"]}<br>
                        <small><i>Personality Mode: {trait.replace('_',' ').title()}</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Simple analytics
        st.markdown("---")
        st.metric("Total Messages", len(st.session_state.chat_history))