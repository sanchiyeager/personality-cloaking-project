# app.py
# Streamlit Command Center for Persona Cloak (Manisha - Frontend)
#
# Run: pip install streamlit plotly requests
# then: streamlit run app.py

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import json

st.set_page_config(page_title="Persona Cloak — Command Center", layout="wide")

# -------------------------
# Config: set this to your backend API when available
# -------------------------
BACKEND_API_URL = "http://localhost:8000/generate_bait_profile"  # change when backend ready
USE_BACKEND = False  # flip True to call real backend

# -------------------------
# Mock generator (used when backend not ready)
# -------------------------
import random
def mock_generate_bait_profile():
    names = ["Asha Rao", "Ravi Menon", "Sana Kapoor", "Irfan Sheikh", "Priya Das"]
    bio_templates = [
        "I love trying out new food trucks and sketching in the park. Currently learning web dev.",
        "Design lead by day, amateur guitarist by night. Always looking for new coffee spots.",
        "Graduate student in CS. Passionate about NLP, long runs and indie films.",
        "Freelance photographer traveling across small towns, caffeinated and curious.",
    ]
    bio = random.choice(bio_templates)
    # personality values between 0 and 1 (Big Five)
    personality = {
        "openness": round(random.uniform(0.2, 0.95), 2),
        "conscientiousness": round(random.uniform(0.1, 0.9), 2),
        "extraversion": round(random.uniform(0.05, 0.9), 2),
         "agreeableness": round(random.uniform(0.15, 0.95), 2),
        "neuroticism": round(random.uniform(0.05, 0.85), 2),
    }
    return {"bio": bio, "personality": personality}

# -------------------------
# Helper: call backend or mock
# -------------------------
def get_bait_profile():
    if USE_BACKEND:
        try:
            resp = requests.post(BACKEND_API_URL, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            st.error(f"Error calling backend: {e}")
            return None
    else:
        return mock_generate_bait_profile()

# -------------------------
# UI layout
# -------------------------
st.title("🛡 Persona Cloak — Command Center")
st.write("Generate bait profiles and inspect their personality scores (Big Five).")

col1, col2 = st.columns([2, 3])

with col1:
    st.header("Controls")
    st.write("Click the button to generate a new bait profile.")
    if st.button("Generate Bait Profile"):
        with st.spinner("Generating..."):
            data = get_bait_profile()
            if data:
                # Normalize trait order and save to session history
                processed = {
                    "bio": data.get("bio", ""),
                    "personality": {
                        "openness": data["personality"].get
                         "conscientiousness": data["personality"].get("conscientiousness", 0),
                        "extraversion": data["personality"].get("extraversion", 0),
                        "agreeableness": data["personality"].get("agreeableness", 0),
                        "neuroticism": data["personality"].get("neuroticism", 0),
                    },
                    "generated_at": datetime.utcnow().isoformat() + "Z"
                }
                # store in session state
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.insert(0, processed)
                st.success("Bait profile generated and saved to history.")
    st.markdown("---")
    st.subheader("Options")
    st.checkbox("Use real backend", value=USE_BACKEND, key="use_backend_checkbox")
    # sync the flag (if user toggles)
    if st.session_state.use_backend_checkbox != USE_BACKEND:
        # show hint
        st.info("Toggle USE_BACKEND flag in code or update BACKEND_API_URL to enable backend calls.")
    st.write("Backend URL:")
    st.text_input("Backend API URL", value=BACKEND_API_URL, key="backend_url_input")

with col2:
    st.header("Latest Generated Profile")
    if "history" in st.session_state and st.session_state.history:
        latest = st.session_state.history[0]
        st.subheader("Bio")
        st.info(latest["bio"])
        st.write("Generated at:", latest["generated_at"])

        # personality table
        st.subheader("Personality Scores (Big Five)")
        scores = latest["personality"]
        # show as two-column table
        cols = st.columns(5)
        for i, (k, v) in enumerate(scores.items()):
            cols[i].metric(k.capitalize(), f"{v:.2f}")

        # Radar chart (Plotly)
        st.subheader("Radar Chart")
        categories = list(scores.keys())
         values = [scores[c] for c in categories]
        # radar needs closed loop
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig = go.Figure(
            data=[
                go.Scatterpolar(r=values_closed, theta=[c.capitalize() for c in categories_closed],
                                fill='toself', name='Personality')
            ],
            layout=go.Layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=False,
                margin=dict(l=40, r=40, t=30, b=30)
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # download / copy actions
        st.markdown("---")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Copy Bio to Clipboard"):
                st.experimental_set_query_params()  # no-op to allow feedback
                # Streamlit doesn't have clipboard API; show textarea for manual copy
                st.text_area("Copy bio (select and copy)", value=latest["bio"], height=120)
        with col_b:
            if st.download_button("Download Profile (JSON)", data=json.dumps(latest, indent=2), file_name="bait_profile.json"):
                st.success("Download started.")

    else:
        st.info("No profile generated yet. Click 'Generate Bait Profile' to begin.")

st.markdown("---")
st.header("History (most recent first)")
if "history" in st.session_state and st.session_state.history:
    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"{idx+1}. {item['generated_at']}"):
            st.write("Bio:")
            st.write(item["bio"])
            st.write("Personality:")
            st.json(item["personality"])
else:
     st.write("No history yet.")