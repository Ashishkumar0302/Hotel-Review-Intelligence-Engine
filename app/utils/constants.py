from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"

ASPECT_ORDER = [
    "safety",
    "location",
    "culture",
    "business",
    "family",
    "wellness",
    "service",
    "cleanliness",
    "value",
    "accessibility",
    "nightlife",
    "beach",
]

ID_COLUMNS = {
    "profile_id",
    "hotel_id",
    "rank",
    "review_id",
    "traveler_type",
    "year_month",
    "sentence",
    "description",
    "aspect",
    "trend",
    "match_reasons",
    "top_strengths",
    "warnings",
}

PLOTLY_TEMPLATE = "plotly_white"

ASPECT_COLORS = [
    "#255f85",
    "#c75d2c",
    "#2f7d5c",
    "#9a5a96",
    "#d1a12b",
    "#4f6fb5",
    "#b84f65",
    "#4c7a2f",
    "#6f5c9f",
    "#208177",
    "#8c6a2f",
    "#52606d",
]

APP_STYLE = """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    .app-subtitle {
        color: #52606d;
        font-size: 1rem;
        line-height: 1.55;
        max-width: 900px;
        margin-bottom: 1.25rem;
    }
    .soft-note {
        color: #667085;
        font-size: 0.9rem;
        line-height: 1.45;
    }
    .section-kicker {
        color: #52606d;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #dde5ec;
        border-radius: 8px;
        padding: 0.72rem 0.85rem;
        background: #ffffff;
    }
</style>
"""
