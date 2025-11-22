import streamlit as st
import plotly.graph_objects as go

# -----------------------------
# IMPORT Poonam's backend (janus)
# -----------------------------
from main import janus   # <-- This connects your app to the real ML system


# -----------------------------
# Function to get REAL bait profile
# -----------------------------
def get_bait_profile(trait="high_neuroticism"):
    """
    Calls Poonam's janus.generate_bait_profile(trait)
    and converts the result into a dictionary.
    """
    profile = janus.generate_bait_profile(trait)
    return profile.to_dict()



# -----------------------------
# STREAMLIT UI STARTS HERE
# -----------------------------
st.set_page_config(page_title="Persona Cloak Command Center", layout="wide")

st.title("🛡 Persona Cloak — Command Center Dashboard")
st.write("Generate REAL bait profiles based on selected personality traits.")

st.markdown("---")


# -----------------------------
# Dropdown for selecting trait
# -----------------------------
trait = st.selectbox(
    "🎯 Select a target personality trait:",
    [
        "high_neuroticism",
        "low_openness",
        "high_extraversion",
        "low_agreeableness",
        "high_conscientiousness"
          ]
)

st.markdown("---")


# -----------------------------
# Button to generate profile
# -----------------------------
if st.button("✨ Generate Bait Profile"):
    
    with st.spinner("Generating real bait profile..."):
        data = get_bait_profile(trait)

    # --------------------------------
    # Display generated BIO
    # --------------------------------
    st.subheader("📝 Generated Bio")
    st.info(data["bio"])

    st.markdown("---")

    # --------------------------------
    # Display personality scores
    # --------------------------------
    st.subheader("📊 Personality Scores (Big Five)")
    traits = data["personality"]

    # Show as a clean table
    st.json(traits)

     st.markdown("---")

    # --------------------------------
    # Radar Chart
    # --------------------------------
    st.subheader("📈 Radar Chart")

    labels = list(traits.keys())
    values = list(traits.values())

    # Radar chart must form a closed loop
    labels += labels[:1]
    values += values[:1]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=[label.capitalize() for label in labels],
                fill='toself'
            )
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(range=[0, 1], visible=True)
            ),
            showlegend=False
        )
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Click *Generate Bait Profile* to see results.")


