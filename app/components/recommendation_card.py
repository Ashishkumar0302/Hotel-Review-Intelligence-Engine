import pandas as pd
import streamlit as st

from app.components.contradiction_panel import contradiction_lines
from app.utils.recommendation_utils import (
    coerce_list,
    confidence_display,
    format_number,
    hotel_display_name,
    labelize,
    match_display,
    strength_labels,
    trend_display,
)


def render_recommendation_card(
    recommendation: pd.Series,
    fallback_strengths: pd.Series | None = None,
    contradictions: pd.DataFrame | None = None,
    derived_confidence: float | None = None,
    derived_trend: tuple[str, float | None] | None = None,
    hotel_categories: dict[str, str] | None = None,
    profile_priorities: list[str] | None = None,
) -> None:
    hotel_id = recommendation.get("hotel_id", "Unknown hotel")
    rank = recommendation.get("rank", "")
    score = recommendation.get("relevance_score")
    confidence = recommendation.get("confidence_score", derived_confidence)
    trend = recommendation.get("trend", None)
    trend_label, trend_score = derived_trend or ("unknown", None)
    final_trend = trend_label if trend_score is not None else trend if isinstance(trend, str) and trend else trend_label
    confidence_text, confidence_stars = confidence_display(confidence)
    match_text, match_stars = match_display(score)
    title = hotel_display_name(hotel_id, hotel_categories)

    with st.container(border=True):
        left, right = st.columns([1.7, 0.9])
        with left:
            st.subheader(f"#{rank} {title}" if rank != "" else title)
            st.caption(f"Hotel ID: {hotel_id}")
            st.markdown(f"**{match_stars} {format_number(score, 0)} Match Score**")
        with right:
            st.markdown(f"**{confidence_stars}**")
            st.caption(confidence_text)
            st.markdown(trend_display(final_trend, trend_score))

        reasons = [str(reason) for reason in coerce_list(recommendation.get("match_reasons"))]
        priorities = profile_priorities or []
        if priorities:
            st.markdown("**Best for**")
            for priority in priorities[:3]:
                st.markdown(f"✓ {labelize(priority)}-focused travelers")

        if reasons:
            st.markdown("**Match Reasons**")
            for reason in reasons[:4]:
                st.markdown(f"- {reason}")

        strengths = strength_labels(recommendation.get("top_strengths"), fallback_strengths, limit=5)
        if strengths:
            st.markdown("**Strengths**")
            strength_columns = st.columns(min(3, len(strengths)))
            for index, strength in enumerate(strengths[:3]):
                label, _, value = strength.partition(" (")
                with strength_columns[index % len(strength_columns)]:
                    st.metric(label, value.rstrip(")") if value else "")
            for strength in strengths[3:]:
                st.caption(strength)

        warnings = [str(item) for item in coerce_list(recommendation.get("warnings"))]
        contradiction_warnings = contradiction_lines(contradictions if contradictions is not None else pd.DataFrame(), limit=3)
        combined = warnings + contradiction_warnings
        if combined:
            st.markdown("**Warnings**")
            for warning in combined[:5]:
                st.markdown(f"⚠ {warning}")
        else:
            st.caption("No warnings attached to this recommendation.")
