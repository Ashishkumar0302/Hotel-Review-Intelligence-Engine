import pandas as pd
import streamlit as st

from app.utils.recommendation_utils import format_number, labelize


def contradiction_lines(contradictions: pd.DataFrame, limit: int = 4) -> list[str]:
    if contradictions is None or contradictions.empty:
        return []
    lines = []
    for _, row in contradictions.head(limit).iterrows():
        aspect = labelize(row.get("aspect", "aspect"))
        best_for = row.get("best_for", "one traveler segment")
        worst_for = row.get("worst_for", "another segment")
        diff = format_number(row.get("difference"), 2)
        lines.append(f"{aspect}: strongest for {best_for}, weakest for {worst_for} (gap {diff})")
    return lines


def render_contradiction_panel(contradictions: pd.DataFrame, title: str = "Contradiction Warnings", limit: int = 5) -> None:
    lines = contradiction_lines(contradictions, limit)
    if not lines:
        st.caption("No contradiction warnings surfaced for this selection.")
        return
    st.markdown(f"**{title}**")
    for line in lines:
        st.markdown(f"- {line}")
