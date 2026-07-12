import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.utils.constants import ASPECT_COLORS, PLOTLY_TEMPLATE
from app.utils.recommendation_utils import labelize


def empty_figure(message: str = "No data available") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font={"size": 16, "color": "#667085"})
    fig.update_layout(template=PLOTLY_TEMPLATE, height=320, xaxis_visible=False, yaxis_visible=False)
    return fig


def aspect_bar(series: pd.Series, title: str, x_title: str = "Score") -> go.Figure:
    if series is None or series.empty:
        return empty_figure()
    data = (
        pd.to_numeric(series, errors="coerce")
        .dropna()
        .sort_values(ascending=True)
        .rename_axis("aspect")
        .reset_index(name="value")
    )
    data["aspect_label"] = data["aspect"].map(labelize)
    fig = px.bar(
        data,
        x="value",
        y="aspect_label",
        orientation="h",
        title=title,
        color="aspect_label",
        color_discrete_sequence=ASPECT_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(showlegend=False, height=max(320, 32 * len(data) + 120), margin=dict(l=12, r=18, t=56, b=18))
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(title="")
    return fig


def importance_color(value: float) -> str:
    if value >= 0.8:
        return "#2f7d5c"
    if value >= 0.5:
        return "#255f85"
    if value >= 0.2:
        return "#c75d2c"
    return "#8a98a8"


def importance_bar(series: pd.Series, title: str = "Aspect Importance") -> go.Figure:
    if series is None or series.empty:
        return empty_figure()
    data = (
        pd.to_numeric(series, errors="coerce")
        .dropna()
        .sort_values(ascending=True)
        .rename_axis("aspect")
        .reset_index(name="value")
    )
    data["aspect_label"] = data["aspect"].map(labelize)
    colors = [importance_color(value) for value in data["value"]]
    fig = go.Figure(go.Bar(x=data["value"], y=data["aspect_label"], orientation="h", marker_color=colors))
    fig.update_layout(
        title=title,
        template=PLOTLY_TEMPLATE,
        height=max(300, 34 * len(data) + 110),
        margin=dict(l=12, r=18, t=56, b=18),
        showlegend=False,
    )
    fig.update_xaxes(title="Preference weight", range=[0, max(1, float(data["value"].max()) * 1.08)])
    fig.update_yaxes(title="")
    return fig


def alignment_heatmap(profile_values: pd.Series, hotel_values: pd.Series, title: str = "Traveler-Hotel Alignment") -> go.Figure:
    if profile_values is None or hotel_values is None or profile_values.empty or hotel_values.empty:
        return empty_figure()
    profile = pd.to_numeric(profile_values, errors="coerce").dropna().sort_values(ascending=False).head(6)
    aligned_aspects = [aspect for aspect in profile.index if aspect in hotel_values.index]
    if not aligned_aspects:
        return empty_figure("No shared aspect signals")
    traveler = profile.loc[aligned_aspects].astype(float)
    hotel = pd.to_numeric(hotel_values.loc[aligned_aspects], errors="coerce").fillna(0).astype(float)
    hotel_normalized = (hotel / 5.0).clip(0, 1)
    match = (traveler * hotel_normalized).clip(0, 1)
    z = [traveler.tolist(), hotel_normalized.tolist(), match.tolist()]
    text = [
        [f"{value:.2f}" for value in traveler],
        [f"{value:.2f}" for value in hotel],
        [alignment_symbol(value) for value in match],
    ]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[labelize(aspect) for aspect in aligned_aspects],
            y=["Traveler Importance", "Hotel Strength", "Match"],
            text=text,
            texttemplate="%{text}",
            colorscale=[
                [0.0, "#eef2f6"],
                [0.35, "#d9e8f0"],
                [0.7, "#8fc7a8"],
                [1.0, "#2f7d5c"],
            ],
            zmin=0,
            zmax=1,
            hovertemplate="%{y}<br>%{x}: %{z:.2f}<extra></extra>",
            showscale=False,
        )
    )
    fig.update_layout(title=title, template=PLOTLY_TEMPLATE, height=310, margin=dict(l=12, r=18, t=56, b=18))
    return fig


def alignment_symbol(value: float) -> str:
    if value >= 0.55:
        return "🟢"
    if value >= 0.28:
        return "🟡"
    return "⚪"


def aspect_distribution(review_aspects: pd.DataFrame, limit: int = 12) -> go.Figure:
    if review_aspects.empty or "aspect" not in review_aspects.columns:
        return empty_figure()
    counts = review_aspects["aspect"].value_counts().head(limit).sort_values()
    return aspect_bar(counts, "Aspect Distribution", "Mentions")


def monthly_review_trend(monthly_stats: pd.DataFrame) -> go.Figure:
    if monthly_stats.empty or "year_month" not in monthly_stats.columns or "review_count" not in monthly_stats.columns:
        return empty_figure()
    trend = monthly_stats.groupby("year_month", as_index=False).agg(review_count=("review_count", "sum"), avg_rating=("avg_rating", "mean"))
    trend["year_month"] = trend["year_month"].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["year_month"], y=trend["review_count"], mode="lines+markers", name="Reviews"))
    if "avg_rating" in trend.columns:
        fig.add_trace(
            go.Scatter(
                x=trend["year_month"],
                y=trend["avg_rating"],
                mode="lines+markers",
                name="Average rating",
                yaxis="y2",
            )
        )
    fig.update_layout(
        title="Temporal Review Signals",
        template=PLOTLY_TEMPLATE,
        height=380,
        margin=dict(l=12, r=18, t=56, b=18),
        yaxis=dict(title="Reviews"),
        yaxis2=dict(title="Avg rating", overlaying="y", side="right", range=[0, 5]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def hotel_rating_distribution(hotel_stats: pd.DataFrame) -> go.Figure:
    if hotel_stats.empty or "avg_rating" not in hotel_stats.columns:
        return empty_figure()
    fig = px.histogram(
        hotel_stats,
        x="avg_rating",
        nbins=18,
        title="Hotel Rating Distribution",
        color_discrete_sequence=["#255f85"],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(height=340, margin=dict(l=12, r=18, t=56, b=18))
    fig.update_xaxes(title="Average rating")
    fig.update_yaxes(title="Hotels")
    return fig


def category_distribution(categories: dict[str, str]) -> go.Figure:
    if not categories:
        return empty_figure("Hotel category artifact not available")
    data = pd.Series(categories).value_counts().sort_index().reset_index()
    data.columns = ["category", "hotels"]
    fig = px.bar(
        data,
        x="category",
        y="hotels",
        title="Hotel Category Statistics",
        color="category",
        color_discrete_sequence=ASPECT_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(showlegend=False, height=320, margin=dict(l=12, r=18, t=56, b=18))
    fig.update_xaxes(title="")
    fig.update_yaxes(title="Hotels")
    return fig


def top_terms_chart(values: dict[str, int], title: str, limit: int = 12) -> go.Figure:
    if not values:
        return empty_figure()
    series = pd.Series(values).sort_values(ascending=False).head(limit).sort_values()
    return aspect_bar(series, title, "Frequency")
