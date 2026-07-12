import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.components.profile_summary import render_profile_summary
from app.components.radar_chart import render_radar
from app.utils.constants import APP_STYLE
from app.utils.data_loader import load_profile_vectors, load_profiles
from app.utils.recommendation_utils import (
    profile_description,
    profile_options,
    profile_vector,
    top_aspects_from_series,
)
from app.utils.visualization_utils import importance_bar


st.set_page_config(page_title="Profile Explorer", layout="wide")
st.markdown(APP_STYLE, unsafe_allow_html=True)

st.title("Profile Explorer")
st.write("Inspect traveler intent vectors and the aspect priorities that drive recommendations.")

profiles = load_profiles()
vectors = load_profile_vectors()
options = profile_options(profiles, vectors)

if not options:
    st.warning("No traveler profiles were found in the profile artifacts.")
    st.stop()

selected_profile = st.selectbox("Traveler profile", options)
vector = profile_vector(vectors, selected_profile)
description = profile_description(profiles, selected_profile)
top_aspects = top_aspects_from_series(vector, 6)

render_profile_summary(selected_profile, description, top_aspects)

left, right = st.columns([1, 1])
with left:
    render_radar(vector, "Top Traveler Priorities", limit=6)
with right:
    st.plotly_chart(importance_bar(vector.sort_values(ascending=False), "Aspect Importance"), use_container_width=True)
