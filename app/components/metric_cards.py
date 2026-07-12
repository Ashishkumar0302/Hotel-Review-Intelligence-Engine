from collections.abc import Sequence
from typing import Any

import streamlit as st


def render_metric_cards(metrics: Sequence[dict[str, Any]]) -> None:
    if not metrics:
        return
    columns = st.columns(min(len(metrics), 6))
    for index, metric in enumerate(metrics):
        with columns[index % len(columns)]:
            st.metric(
                str(metric.get("label", "")),
                str(metric.get("value", "N/A")),
                help=str(metric.get("help", "")) if metric.get("help") else None,
            )
