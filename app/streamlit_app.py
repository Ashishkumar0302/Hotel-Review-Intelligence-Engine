import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.components.metric_cards import render_metric_cards
from app.utils.constants import APP_STYLE
from app.utils.data_loader import (
    artifact_health,
    load_dataset_metadata,
    load_hotel_confidence_scores,
    load_hotel_stats,
    load_profile_vectors,
    load_recommendations,
    load_review_aspects,
)
from app.utils.recommendation_utils import format_number
from app.utils.visualization_utils import aspect_distribution, hotel_rating_distribution


st.set_page_config(
    page_title="Hotel Review Intelligence Engine",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_STYLE, unsafe_allow_html=True)

st.title("Hotel Review Intelligence Engine")
st.write(
    "Explainable travel intelligence built from review aspects, traveler priorities, "
    "hotel strengths, confidence signals, contradictions, and trends."
)

metadata = load_dataset_metadata()
recommendations = load_recommendations()
profiles = load_profile_vectors()
hotel_stats = load_hotel_stats()
review_aspects = load_review_aspects()
confidence = load_hotel_confidence_scores()

total_recommendations = len(recommendations) if not recommendations.empty else 0
avg_confidence = confidence["confidence_score"].mean() if "confidence_score" in confidence.columns else None
avg_rating = hotel_stats["avg_rating"].mean() if "avg_rating" in hotel_stats.columns else None
aspect_signals = len(review_aspects)

render_metric_cards(
    [
        {"label": "Reviews Processed", "value": f"{metadata.get('num_reviews', len(review_aspects)):,}"},
        {"label": "Aspect Signals Extracted", "value": f"{aspect_signals:,}"},
        {"label": "Hotels Profiled", "value": f"{metadata.get('num_hotels', hotel_stats.get('hotel_id', pd.Series()).nunique()):,}"},
        {"label": "Traveler Personas Modeled", "value": f"{metadata.get('num_profiles', profiles.get('profile_id', pd.Series()).nunique()):,}"},
    ]
)

st.subheader("Capabilities")
capability_cols = st.columns(5)
capabilities = [
    "✓ Aspect-level intelligence",
    "✓ Explainable recommendations",
    "✓ Contradiction detection",
    "✓ Temporal trend analysis",
    "✓ Traveler personalization",
]
for column, capability in zip(capability_cols, capabilities):
    with column:
        st.write(capability)

render_metric_cards(
    [
        {"label": "Recommendation Rows", "value": f"{total_recommendations:,}"},
        {"label": "Avg Hotel Rating", "value": format_number(avg_rating, 2)},
        {"label": "Avg Confidence Signal", "value": format_number(avg_confidence, 2)},
    ]
)

st.subheader("Intelligence Snapshot")
left, right = st.columns([1.05, 1])
with left:
    st.plotly_chart(aspect_distribution(review_aspects), use_container_width=True)
with right:
    st.plotly_chart(hotel_rating_distribution(hotel_stats), use_container_width=True)

with st.expander("Artifact Readiness"):
    health = artifact_health()
    if not health.empty:
        st.dataframe(health, use_container_width=True, hide_index=True)

st.caption("Open the pages in the sidebar to inspect traveler profiles, explainable recommendations, and system-level intelligence.")
