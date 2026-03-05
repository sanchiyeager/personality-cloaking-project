import streamlit as st
import plotly.graph_objects as go
import random
import time
from datetime import datetime

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

if "profile" not in st.session_state:
    st.session_state.profile = "High Neuroticism"

# -----------------------------------
# WHATSAPP STYLE CSS
# -----------------------------------
st.markdown("""
<style>

.chat-container{
    background-color:#efeae2;
    height:520px;
    overflow-y:auto;
    padding:15px;
    border-radius:10px;
}

.message{
    padding:10px 14px;
    border-radius:10px;
    margin-bottom:10px;
    max-width:70%;
    font-size:14px;
}

.user{
    background:#d9fdd3;
    margin-left:auto;
    text-align:right;
}

.ai{
    background:white;
    margin-right:auto;
}

.time{
    font-size:10px;
    color:gray;
}

.header{
    background:#075E54;
    color:white;
    padding:12px;
    border-radius:8px;
    margin-bottom:10px;
}

.input-box{
    margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# PROFILES
# -----------------------------------
PROFILES = {
    "High Neuroticism": {
        "bio":"I usually worry about online risks and verify information before trusting messages.",
        "traits":{
            "Openness":0.4,
            "Conscientiousness":0.7,
            "Extraversion":0.3,
            "Agreeableness":0.55,
            "Neuroticism":0.85
        },
        "replies":[
            "I feel unsure about this.",
            "This seems risky.",
            "Can you explain more?"
        ]
    },

    "High Extraversion": {
        "bio":"I enjoy chatting with people online and responding quickly.",
        "traits":{
            "Openness":0.7,
            "Conscientiousness":0.5,
            "Extraversion":0.9,
            "Agreeableness":0.65,
            "Neuroticism":0.3
        },
        "replies":[
            "Oh interesting 😄",
            "Tell me more!",
            "That sounds exciting!"
        ]
    },

    "High Conscientiousness":{
        "bio":"I prefer structured conversations and verified information.",
        "traits":{
            "Openness":0.5,
            "Conscientiousness":0.9,
            "Extraversion":0.4,
            "Agreeableness":0.6,
            "Neuroticism":0.3
        },
        "replies":[
            "Please provide verification.",
            "I need proper documentation.",
            "Can you share official proof?"
        ]
    }
}

# -----------------------------------
# PROFILE SELECTOR
# -----------------------------------
profile = st.selectbox(
    "Select Personality Profile",
    list(PROFILES.keys())
)

data = PROFILES[profile]

# -----------------------------------
# LAYOUT
# -----------------------------------
left, right = st.columns([1,2])

# -----------------------------------
# LEFT PANEL (PROFILE)
# -----------------------------------
with left:

    st.subheader("🧠 Persona Profile")

    st.markdown("### Bio")
    st.write(data["bio"])

    st.markdown("### Big Five Traits")

    fig = go.Figure(
        data=[go.Bar(
            x=list(data["traits"].keys()),
            y=list(data["traits"].values())
        )]
    )

    fig.update_layout(
        height=300,
        yaxis=dict(range=[0,1]),
        margin=dict(l=10,r=10,t=10,b=10)
    )

    st.plotly_chart(fig,use_container_width=True)

# -----------------------------------
# RIGHT PANEL (WHATSAPP CHAT)
# -----------------------------------
with right:

    st.markdown(
        f'<div class="header">💬 Chatting with Persona ({profile})</div>',
        unsafe_allow_html=True
    )

    chat_html = '<div class="chat-container">'

    for msg in st.session_state.messages:

        if msg["role"]=="user":
            bubble="user"
        else:
            bubble="ai"

        chat_html += f"""
        <div class="message {bubble}">
        {msg["content"]}
        <div class="time">{msg["time"]}</div>
        </div>
        """

    chat_html += "</div>"

    st.markdown(chat_html, unsafe_allow_html=True)

    # -----------------------------------
    # INPUT BOX
    # -----------------------------------
    user_input = st.text_input("Type message", key="input")

    if st.button("Send"):

        if user_input.strip()!="":

            now=datetime.now().strftime("%H:%M")

            st.session_state.messages.append({
                "role":"user",
                "content":user_input,
                "time":now
            })

            # AI thinking
            time.sleep(random.randint(1,2))

            reply=random.choice(data["replies"])

            now=datetime.now().strftime("%H:%M")

            st.session_state.messages.append({
                "role":"ai",
                "content":reply,
                "time":now
            })

            st.rerun()

    st.markdown("---")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages=[]
        st.rerun()
