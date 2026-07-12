import pandas as pd
import streamlit as st

from app.utils.recommendation_utils import format_number, labelize


def render_profile_summary(profile_id: str, description: str, top_aspects: pd.Series) -> None:
    with st.container(border=True):
        st.caption("Traveler Profile")
        st.subheader(str(profile_id))
        st.write(description or "No profile description is available in the artifact.")
        if top_aspects is not None and not top_aspects.empty:
            columns = st.columns(min(5, len(top_aspects)))
            for index, (aspect, value) in enumerate(top_aspects.items()):
                with columns[index % len(columns)]:
                    st.metric(labelize(aspect), format_number(value, 2))
