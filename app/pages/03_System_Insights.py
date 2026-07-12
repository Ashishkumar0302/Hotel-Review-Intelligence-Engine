import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.components.contradiction_panel import render_contradiction_panel
from app.components.metric_cards import render_metric_cards
from app.utils.constants import APP_STYLE
from app.utils.data_loader import (
    load_dataset_metadata,
    load_hotel_categories,
    load_hotel_contradictions,
    load_hotel_stats,
    load_monthly_hotel_stats,
    load_review_aspects,
    load_top_bigrams,
    load_top_words,
)
from app.utils.recommendation_utils import format_number
from app.utils.visualization_utils import (
    aspect_distribution,
    category_distribution,
    hotel_rating_distribution,
    monthly_review_trend,
    top_terms_chart,
)


st.set_page_config(page_title="System Insights", layout="wide")
st.markdown(APP_STYLE, unsafe_allow_html=True)

st.title("System Insights")
st.write("A system-level view of review coverage, aspect prevalence, temporal movement, category mix, and contradiction signals.")

metadata = load_dataset_metadata()
review_aspects = load_review_aspects()
hotel_stats = load_hotel_stats()
monthly_stats = load_monthly_hotel_stats()
contradictions = load_hotel_contradictions()
top_words = load_top_words()
top_bigrams = load_top_bigrams()
categories = load_hotel_categories()

review_count = metadata.get("num_reviews", review_aspects.get("review_id", pd.Series()).nunique())
hotel_count = metadata.get("num_hotels", hotel_stats.get("hotel_id", pd.Series()).nunique())
aspect_mentions = len(review_aspects)
avg_reviews_per_hotel = hotel_stats["review_count"].mean() if "review_count" in hotel_stats.columns else None
avg_rating = hotel_stats["avg_rating"].mean() if "avg_rating" in hotel_stats.columns else None

render_metric_cards(
    [
        {"label": "Reviews", "value": f"{int(review_count):,}" if pd.notna(review_count) else "N/A"},
        {"label": "Aspect Mentions", "value": f"{aspect_mentions:,}"},
        {"label": "Hotels", "value": f"{int(hotel_count):,}" if pd.notna(hotel_count) else "N/A"},
        {"label": "Reviews / Hotel", "value": format_number(avg_reviews_per_hotel, 1)},
        {"label": "Avg Rating", "value": format_number(avg_rating, 2)},
        {"label": "Contradictions", "value": f"{len(contradictions):,}"},
    ]
)

tab_overview, tab_terms, tab_contradictions = st.tabs(["Signals", "Language", "Contradictions"])

with tab_overview:
    top_left, top_right = st.columns([1, 1])
    with top_left:
        st.plotly_chart(aspect_distribution(review_aspects), use_container_width=True)
    with top_right:
        st.plotly_chart(monthly_review_trend(monthly_stats), use_container_width=True)

    bottom_left, bottom_right = st.columns([1, 1])
    with bottom_left:
        st.plotly_chart(hotel_rating_distribution(hotel_stats), use_container_width=True)
    with bottom_right:
        st.plotly_chart(category_distribution(categories), use_container_width=True)

with tab_terms:
    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(top_terms_chart(top_words, "Most Common Review Terms"), use_container_width=True)
    with right:
        st.plotly_chart(top_terms_chart(top_bigrams, "Most Common Review Bigrams"), use_container_width=True)

with tab_contradictions:
    if contradictions.empty:
        st.info("No contradiction artifact data is available.")
    else:
        selected_hotel = st.selectbox("Hotel", sorted(contradictions["hotel_id"].astype(str).unique()))
        scoped = contradictions[contradictions["hotel_id"].astype(str) == selected_hotel]
        render_contradiction_panel(scoped, title=f"Contradiction Examples for {selected_hotel}", limit=8)
        st.dataframe(scoped, use_container_width=True, hide_index=True)
