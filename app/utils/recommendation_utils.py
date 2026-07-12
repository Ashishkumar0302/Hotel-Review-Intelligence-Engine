import ast
import json
from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd


def labelize(value: Any) -> str:
    return str(value).replace("_", " ").title()


def format_number(value: Any, digits: int = 1, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return str(value)


def score_to_five(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return min(5.0, max(1.0, float(value) / 20.0))
    except (TypeError, ValueError):
        return None


def stars_for_score(score: float | None) -> str:
    if score is None:
        return "☆☆☆☆☆"
    filled = int(round(min(5, max(0, score))))
    return "★" * filled + "☆" * (5 - filled)


def confidence_display(value: Any) -> tuple[str, str]:
    score = score_to_five(value)
    if score is None:
        return ("Confidence unavailable", "☆☆☆☆☆")
    if score >= 4:
        label = "High Confidence"
    elif score >= 3:
        label = "Medium Confidence"
    else:
        label = "Low Confidence"
    return (f"{score:.1f} / 5 {label}", stars_for_score(score))


def match_display(value: Any) -> tuple[str, str]:
    score = score_to_five(value)
    if score is None:
        return ("Match score unavailable", "☆☆☆☆☆")
    return (f"{score:.1f} / 5 Match Score", stars_for_score(score))


def trend_display(label: str, score: float | None = None) -> str:
    normalized = str(label or "unknown").lower()
    if normalized == "improving":
        prefix = "🟢 Improving"
    elif normalized == "declining":
        prefix = "🔴 Declining"
    elif normalized == "stable":
        prefix = "🟡 Stable"
    else:
        prefix = "⚪ Trend unavailable"
    if score is None or pd.isna(score):
        return prefix
    percent = int(round(float(score) * 100))
    if percent == 0:
        return prefix
    sign = "+" if percent > 0 else ""
    return f"{prefix} ({sign}{percent}%)"


def hotel_display_name(
    hotel_id: Any,
    categories: dict[str, str] | None = None,
    hotel_metadata: dict[str, dict[str, Any]] | None = None,
) -> str:
    hotel_key = str(hotel_id)
    metadata = (hotel_metadata or {}).get(hotel_key, {})
    name = metadata.get("hotel_name", hotel_key)
    category = metadata.get("hotel_category") or (categories or {}).get(hotel_key)
    return f"{name} • {category}" if category else f"{name} • {hotel_key}"


def hotel_metadata_fields(
    hotel_id: Any,
    hotel_metadata: dict[str, dict[str, Any]] | None = None,
    categories: dict[str, str] | None = None,
) -> dict[str, Any]:
    hotel_key = str(hotel_id)
    metadata = (hotel_metadata or {}).get(hotel_key, {})
    return {
        "hotel_name": metadata.get("hotel_name", hotel_key),
        "hotel_category": metadata.get("hotel_category") or (categories or {}).get(hotel_key, "Unknown"),
    }


def desired_dimensions_for_profile(profile_values: pd.Series, limit: int = 3) -> list[str]:
    aliases = {
        "culture": "local_culture",
        "location": "location_central",
    }
    dimensions = [aliases.get(aspect, str(aspect)) for aspect in top_aspects_from_series(profile_values, limit).index]
    preferred_order = ["safety", "local_culture", "location_central"]
    ordered = [dimension for dimension in preferred_order if dimension in dimensions]
    ordered.extend(dimension for dimension in dimensions if dimension not in ordered)
    return ordered


def profile_archetype(profile_id: str, description: str, desired_dims: list[str]) -> str:
    text = f"{profile_id} {description} {' '.join(desired_dims)}".lower()
    pieces = []
    if "solo" in text:
        pieces.append("solo")
    if "female" in text or "safety" in desired_dims:
        pieces.append("female")
    if "culture" in text:
        pieces.append("culture")
    if not pieces:
        pieces = [profile_id.lower()]
    return "_".join(pieces)


def recommendation_schema_payload(
    profile_id: str,
    description: str,
    profile_values: pd.Series,
    recommendations: pd.DataFrame,
    hotel_metadata: dict[str, dict[str, Any]] | None = None,
    categories: dict[str, str] | None = None,
) -> dict[str, Any]:
    desired_dims = desired_dimensions_for_profile(profile_values)
    top_hotels = []
    for _, row in recommendations.iterrows():
        hotel_id = str(row.get("hotel_id", ""))
        metadata = hotel_metadata_fields(hotel_id, hotel_metadata, categories)
        score = row.get("score", row.get("relevance_score"))
        top_hotels.append(
            {
                "rank": int(row.get("rank", len(top_hotels) + 1)),
                "hotel_id": hotel_id,
                "hotel_name": metadata["hotel_name"],
                "hotel_category": metadata["hotel_category"],
                "score": round(float(score), 3) if score is not None and not pd.isna(score) else None,
            }
        )
    return {
        "profile_id": str(profile_id),
        "archetype": profile_archetype(profile_id, description, desired_dims),
        "desired_dims": desired_dims,
        "top_hotels": top_hotels,
    }


def compact_description(text: Any, limit: int = 105) -> str:
    value = "" if text is None or pd.isna(text) else str(text)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def coerce_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(stripped)
                if isinstance(parsed, (list, tuple, set, np.ndarray)):
                    return list(parsed)
            except (ValueError, SyntaxError, TypeError, json.JSONDecodeError):
                continue
        return [stripped]
    if isinstance(value, Iterable) and not isinstance(value, (dict, bytes)):
        return list(value)
    return [value]


def coerce_records(value: Any) -> list[dict[str, Any]]:
    records = []
    for item in coerce_list(value):
        if isinstance(item, dict):
            records.append(item)
        elif isinstance(item, str):
            records.append({"label": item})
        else:
            records.append({"label": str(item)})
    return records


def profile_options(profiles: pd.DataFrame, vectors: pd.DataFrame) -> list[str]:
    candidates: list[str] = []
    for frame in (profiles, vectors):
        if "profile_id" in frame.columns:
            candidates.extend(frame["profile_id"].dropna().astype(str).tolist())
    return sorted(set(candidates))


def profile_description(profiles: pd.DataFrame, profile_id: str) -> str:
    if profiles.empty or "profile_id" not in profiles.columns or "description" not in profiles.columns:
        return ""
    match = profiles.loc[profiles["profile_id"].astype(str) == str(profile_id), "description"]
    return "" if match.empty else str(match.iloc[0])


def profile_vector(vectors: pd.DataFrame, profile_id: str) -> pd.Series:
    if vectors.empty or "profile_id" not in vectors.columns:
        return pd.Series(dtype=float)
    row = vectors.loc[vectors["profile_id"].astype(str) == str(profile_id)]
    if row.empty:
        return pd.Series(dtype=float)
    return row.iloc[0].drop(labels=["profile_id"], errors="ignore").astype(float)


def top_aspects_from_series(series: pd.Series, limit: int = 5) -> pd.Series:
    if series.empty:
        return series
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    return numeric.sort_values(ascending=False).head(limit)


def recommendations_for_profile(recommendations: pd.DataFrame, profile_id: str, limit: int = 5) -> pd.DataFrame:
    if recommendations.empty or "profile_id" not in recommendations.columns:
        return pd.DataFrame()
    scoped = recommendations[recommendations["profile_id"].astype(str) == str(profile_id)].copy()
    if scoped.empty:
        return scoped
    sort_cols = [col for col in ["rank", "relevance_score"] if col in scoped.columns]
    ascending = [True if col == "rank" else False for col in sort_cols]
    if sort_cols:
        scoped = scoped.sort_values(sort_cols, ascending=ascending)
    return scoped.head(limit)


def hotel_aspect_scores(hotel_matrix: pd.DataFrame, hotel_id: str, limit: int = 5) -> pd.Series:
    if hotel_matrix.empty:
        return pd.Series(dtype=float)
    matrix = hotel_matrix.copy()
    if "hotel_id" in matrix.columns:
        row = matrix[matrix["hotel_id"].astype(str) == str(hotel_id)]
        if row.empty:
            return pd.Series(dtype=float)
        series = row.iloc[0].drop(labels=["hotel_id"], errors="ignore")
    else:
        key = str(hotel_id)
        if key not in matrix.index.astype(str):
            return pd.Series(dtype=float)
        series = matrix.loc[matrix.index.astype(str) == key].iloc[0]
    return top_aspects_from_series(series, limit)


def confidence_for_hotel(confidence_scores: pd.DataFrame, hotel_id: str) -> float | None:
    if confidence_scores.empty or "hotel_id" not in confidence_scores.columns:
        return None
    match = confidence_scores[confidence_scores["hotel_id"].astype(str) == str(hotel_id)]
    if match.empty or "confidence_score" not in match.columns:
        return None
    return float(match.iloc[0]["confidence_score"])


def trend_for_hotel(trends: pd.DataFrame, hotel_id: str, focus_aspects: list[str] | None = None) -> tuple[str, float | None]:
    if trends.empty or "hotel_id" not in trends.columns or "trend_score" not in trends.columns:
        return ("unknown", None)
    scoped = trends[trends["hotel_id"].astype(str) == str(hotel_id)]
    if focus_aspects and "aspect" in scoped.columns:
        focused = scoped[scoped["aspect"].astype(str).isin(focus_aspects)]
        if not focused.empty:
            scoped = focused
    if scoped.empty:
        return ("unknown", None)
    score = float(pd.to_numeric(scoped["trend_score"], errors="coerce").dropna().mean())
    if score >= 0.08:
        return ("improving", score)
    if score <= -0.08:
        return ("declining", score)
    return ("stable", score)


def contradictions_for_hotel(contradictions: pd.DataFrame, hotel_id: str, limit: int = 4) -> pd.DataFrame:
    if contradictions.empty or "hotel_id" not in contradictions.columns:
        return pd.DataFrame()
    scoped = contradictions[contradictions["hotel_id"].astype(str) == str(hotel_id)].copy()
    if "difference" in scoped.columns:
        scoped = scoped.sort_values("difference", ascending=False)
    return scoped.head(limit)


def strength_labels(records: Any, fallback_scores: pd.Series | None = None, limit: int = 4) -> list[str]:
    strengths = []
    for record in coerce_records(records):
        aspect = record.get("aspect") or record.get("label")
        score = record.get("score")
        if aspect and score is not None:
            strengths.append(f"{labelize(aspect)} ({format_number(score, 2)})")
        elif aspect:
            strengths.append(labelize(aspect))
    if not strengths and fallback_scores is not None and not fallback_scores.empty:
        strengths = [f"{labelize(aspect)} ({format_number(score, 2)})" for aspect, score in fallback_scores.items()]
    return strengths[:limit]
