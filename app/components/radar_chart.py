import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.constants import PLOTLY_TEMPLATE
from app.utils.recommendation_utils import labelize
from app.utils.visualization_utils import empty_figure


def radar_figure(values: pd.Series, title: str = "Preference Radar", limit: int = 6) -> go.Figure:
    if values is None or values.empty:
        return empty_figure()
    series = pd.to_numeric(values, errors="coerce").dropna().sort_values(ascending=False).head(limit)
    if series.empty:
        return empty_figure()
    theta = [labelize(item) for item in series.index.tolist()]
    r_values = series.astype(float).tolist()
    theta.append(theta[0])
    r_values.append(r_values[0])
    max_range = max(1.0, max(r_values) * 1.15)
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=r_values,
                theta=theta,
                fill="toself",
                line=dict(color="#255f85", width=3),
                fillcolor="rgba(37, 95, 133, 0.22)",
                name="Preference",
            )
        ]
    )
    fig.update_layout(
        title=title,
        template=PLOTLY_TEMPLATE,
        height=440,
        margin=dict(l=28, r=28, t=62, b=28),
        polar=dict(radialaxis=dict(visible=True, range=[0, max_range])),
        showlegend=False,
    )
    return fig


def render_radar(values: pd.Series, title: str = "Preference Radar", limit: int = 6) -> None:
    st.plotly_chart(radar_figure(values, title, limit), use_container_width=True)
