import streamlit as st
import plotly.graph_objects as go
import random
import time
from datetime import datetime

st.set_page_config(layout="wide")

# -----------------------------------
# CUSTOM CSS (WhatsApp Style)
# -----------------------------------
st.markdown("""
<style>

body {
    background-color:#ece5dd;
}

.chat-container{
    height:500px;
    overflow-y:auto;
    padding:10px;
    background:#e5ddd5;
    border-radius:10px;
}

.user-msg{
    background:#dcf8c6;
    padding:8px 12px;
    border-radius:10px;
    margin:5px;
    width:fit-content;
    margin-left:auto;
}

.ai-msg{
    background:white;
    padding:8px 12px;
    border-radius:10px;
    margin:5px;
    width:fit-content;
}

.chat-header{
    background:#075e54;
    color:white;
    padding:12px;
    border-radius:8px;
    font-weight:bold;
}

.sidebar-contact{
    padding:10px;
    border-bottom:1px solid #ddd;
}

.sidebar-contact:hover{
    background:#f0f0f0;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# PERSONA DATABASE
# -----------------------------------

PERSONAS = {

"Neurotic Persona":{
"bio":"I worry about online risks and verify information carefully.",
"traits":{
"Openness":0.42,
"Conscientiousness":0.78,
"Extraversion":0.31,
"Agreeableness":0.56,
"Neuroticism":0.74
},
"replies":[
"This feels risky.",
"I’m not comfortable with this.",
"Can you explain more?",
"I need to verify this."
]
},

"Extravert Persona":{
"bio":"I enjoy talking and interacting online.",
"traits":{
"Openness":0.7,
"Conscientiousness":0.5,
"Extraversion":0.9,
"Agreeableness":0.6,
"Neuroticism":0.3
},
"replies":[
"Hey that sounds fun!",
"Interesting 😄",
"Tell me more!"
]
},

"Conscientious Persona":{
"bio":"I prefer secure and verified communication.",
"traits":{
"Openness":0.5,
"Conscientiousness":0.9,
"Extraversion":0.4,
"Agreeableness":0.6,
"Neuroticism":0.3
},
"replies":[
"I need verification first.",
"Please share official proof.",
"This requires confirmation."
]
}

}

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "current_chat" not in st.session_state:
    st.session_state.current_chat=list(PERSONAS.keys())[0]

if "messages" not in st.session_state:
    st.session_state.messages={p:[] for p in PERSONAS}

if "show_graph" not in st.session_state:
    st.session_state.show_graph=False

# -----------------------------------
# LAYOUT
# -----------------------------------

left,right=st.columns([1,3])

# -----------------------------------
# LEFT SIDEBAR (PERSONA LIST)
# -----------------------------------

with left:

    st.subheader("Personas")

    for persona in PERSONAS:

        col1,col2=st.columns([4,1])

        with col1:

            if st.button(persona,key=persona,use_container_width=True):

                st.session_state.current_chat=persona

        with col2:

            if st.button("📊",key=persona+"graph"):

                st.session_state.show_graph=True
                st.session_state.graph_persona=persona

# -----------------------------------
# RIGHT CHAT WINDOW
# -----------------------------------

with right:

    persona=st.session_state.current_chat
    data=PERSONAS[persona]

    st.markdown(
        f'<div class="chat-header">💬 {persona}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="chat-container">',unsafe_allow_html=True)

    for msg in st.session_state.messages[persona]:

        if msg["role"]=="user":

            st.markdown(
            f'<div class="user-msg">{msg["text"]}<br><small>{msg["time"]}</small></div>',
            unsafe_allow_html=True
            )

        else:

            st.markdown(
            f'<div class="ai-msg">{msg["text"]}<br><small>{msg["time"]}</small></div>',
            unsafe_allow_html=True
            )

    st.markdown('</div>',unsafe_allow_html=True)

    user_input=st.text_input("Type message")

    if st.button("Send"):

        if user_input!="":

            now=datetime.now().strftime("%H:%M")

            st.session_state.messages[persona].append({
            "role":"user",
            "text":user_input,
            "time":now
            })

            time.sleep(1)

            reply=random.choice(data["replies"])

            st.session_state.messages[persona].append({
            "role":"ai",
            "text":reply,
            "time":now
            })

            st.rerun()

# -----------------------------------
# GRAPH POPUP
# -----------------------------------

if st.session_state.show_graph:

    persona=st.session_state.graph_persona
    traits=PERSONAS[persona]["traits"]

    st.subheader(f"{persona} Personality Traits")

    fig=go.Figure(
        data=[
            go.Scatterpolar(
            r=list(traits.values()),
            theta=list(traits.keys()),
            fill='toself'
            )
        ]
    )

    fig.update_layout(
    polar=dict(radialaxis=dict(range=[0,1])),
    height=400
    )

    st.plotly_chart(fig,use_container_width=True)

    if st.button("Close Graph"):

        st.session_state.show_graph=False
