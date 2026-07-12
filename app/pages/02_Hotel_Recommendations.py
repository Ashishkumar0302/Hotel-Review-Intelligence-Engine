import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.components.metric_cards import render_metric_cards
from app.utils.constants import APP_STYLE
from app.utils.data_loader import (
    load_hotel_categories,
    load_hotel_metadata,
    load_profile_vectors,
    load_profiles,
    load_recommendations,
)
from app.utils.recommendation_utils import (
    profile_description,
    profile_options,
    profile_vector,
    recommendation_schema_payload,
    recommendations_for_profile,
)


st.set_page_config(page_title="Hotel Recommendations", layout="wide")
st.markdown(APP_STYLE, unsafe_allow_html=True)

st.title("Hotel Recommendations")
st.write("Top hotels are shown in the recommendation schema and enriched with names and categories from hotel_reviews.json.")

profiles = load_profiles()
vectors = load_profile_vectors()
recommendations = load_recommendations()
categories = load_hotel_categories()
hotel_metadata = load_hotel_metadata()

options = profile_options(profiles, vectors)
if not options:
    st.warning("No traveler profiles were found in the profile artifacts.")
    st.stop()

selected_profile = st.selectbox("Traveler profile", options)
vector = profile_vector(vectors, selected_profile)
description = profile_description(profiles, selected_profile)
profile_recs = recommendations_for_profile(recommendations, selected_profile, 5)

if profile_recs.empty:
    st.warning("No recommendations were found for this profile in recommendations.parquet.")
    st.stop()

schema_payload = recommendation_schema_payload(
    selected_profile,
    description,
    vector,
    profile_recs,
    hotel_metadata=hotel_metadata,
    categories=categories,
)

render_metric_cards(
    [
        {"label": "Profile ID", "value": schema_payload["profile_id"]},
        {"label": "Archetype", "value": schema_payload["archetype"]},
        {"label": "Desired Dimensions", "value": str(len(schema_payload["desired_dims"]))},
        {"label": "Top Hotels", "value": str(len(schema_payload["top_hotels"]))},
    ]
)

st.subheader("Desired Dimensions")
st.write(", ".join(schema_payload["desired_dims"]))

st.subheader("Top Hotels")
st.dataframe(schema_payload["top_hotels"], use_container_width=True, hide_index=True)

st.subheader("Schema Payload")
st.json(schema_payload)
