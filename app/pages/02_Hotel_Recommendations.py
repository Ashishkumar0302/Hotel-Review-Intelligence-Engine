import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.components.metric_cards import render_metric_cards
from app.components.profile_summary import render_profile_summary
from app.components.recommendation_card import render_recommendation_card
from app.components.radar_chart import render_radar
from app.utils.constants import APP_STYLE
from app.utils.data_loader import (
    load_hotel_confidence_scores,
    load_hotel_contradictions,
    load_hotel_categories,
    load_hotel_matrix,
    load_hotel_trends,
    load_profile_vectors,
    load_profiles,
    load_recommendations,
)
from app.utils.recommendation_utils import (
    coerce_list,
    confidence_for_hotel,
    contradictions_for_hotel,
    format_number,
    hotel_aspect_scores,
    hotel_display_name,
    profile_description,
    profile_options,
    profile_vector,
    recommendations_for_profile,
    top_aspects_from_series,
    trend_for_hotel,
)
from app.utils.visualization_utils import alignment_heatmap, importance_bar


st.set_page_config(page_title="Hotel Recommendations", layout="wide")
st.markdown(APP_STYLE, unsafe_allow_html=True)

st.title("Hotel Recommendations")
st.write("Top hotels are shown exactly from the recommendation artifact, with confidence, trend, strengths, and contradictions attached from the intelligence layer.")

profiles = load_profiles()
vectors = load_profile_vectors()
recommendations = load_recommendations()
hotel_matrix = load_hotel_matrix()
confidence_scores = load_hotel_confidence_scores()
contradictions = load_hotel_contradictions()
trends = load_hotel_trends()
categories = load_hotel_categories()

options = profile_options(profiles, vectors)
if not options:
    st.warning("No traveler profiles were found in the profile artifacts.")
    st.stop()

selected_profile = st.selectbox("Traveler profile", options)
vector = profile_vector(vectors, selected_profile)
description = profile_description(profiles, selected_profile)
top_aspects = top_aspects_from_series(vector, 6)
top_aspect_names = top_aspects.index.astype(str).tolist()
profile_recs = recommendations_for_profile(recommendations, selected_profile, 5)

render_profile_summary(selected_profile, description, top_aspects)

if profile_recs.empty:
    st.warning("No recommendations were found for this profile in recommendations.parquet.")
    st.stop()

warning_count = int(profile_recs.get("warnings").apply(lambda value: len(coerce_list(value))).sum()) if "warnings" in profile_recs.columns else 0
render_metric_cards(
    [
        {"label": "Hotels Shown", "value": str(len(profile_recs))},
        {"label": "Avg Relevance", "value": format_number(profile_recs.get("relevance_score").mean(), 2)},
        {"label": "Best Score", "value": format_number(profile_recs.get("relevance_score").max(), 2)},
        {"label": "Warnings", "value": str(warning_count)},
    ]
)

radar_col, importance_col = st.columns([1, 1])
with radar_col:
    render_radar(vector, "Top Traveler Priorities", limit=6)
with importance_col:
    st.plotly_chart(importance_bar(vector.sort_values(ascending=False), "Aspect Importance"), use_container_width=True)

st.subheader("Traveler-Hotel Alignment")
alignment_labels = [
    f"#{row.get('rank', '')} {hotel_display_name(row.get('hotel_id'), categories)}"
    for _, row in profile_recs.iterrows()
]
selected_alignment = st.selectbox("Inspect alignment for", alignment_labels)
alignment_index = alignment_labels.index(selected_alignment)
alignment_rec = profile_recs.iloc[alignment_index]
alignment_hotel_id = str(alignment_rec.get("hotel_id", ""))
alignment_scores = hotel_aspect_scores(hotel_matrix, alignment_hotel_id, 12)
st.plotly_chart(
    alignment_heatmap(vector, alignment_scores, f"Why {hotel_display_name(alignment_hotel_id, categories)} fits {selected_profile}"),
    use_container_width=True,
)

st.subheader("Top Recommendations")
for _, rec in profile_recs.iterrows():
    hotel_id = str(rec.get("hotel_id", ""))
    fallback_strengths = hotel_aspect_scores(hotel_matrix, hotel_id, 5)
    rec_contradictions = contradictions_for_hotel(contradictions, hotel_id, 4)
    rec_confidence = confidence_for_hotel(confidence_scores, hotel_id)
    rec_trend = trend_for_hotel(trends, hotel_id, top_aspect_names)
    render_recommendation_card(
        rec,
        fallback_strengths=fallback_strengths,
        contradictions=rec_contradictions,
        derived_confidence=rec_confidence,
        derived_trend=rec_trend,
        hotel_categories=categories,
        profile_priorities=top_aspect_names,
    )
