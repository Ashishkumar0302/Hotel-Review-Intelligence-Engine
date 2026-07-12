import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from app.utils.constants import ARTIFACT_DIR, ASPECT_ORDER, ID_COLUMNS


def artifact_path(filename: str) -> Path:
    return ARTIFACT_DIR / filename


@st.cache_data(show_spinner=False)
def load_parquet(filename: str) -> pd.DataFrame:
    path = artifact_path(filename)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@st.cache_data(show_spinner=False)
def load_json(filename: str) -> dict[str, Any]:
    path = artifact_path(filename)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data(show_spinner=False)
def load_numpy(filename: str) -> np.ndarray:
    path = artifact_path(filename)
    if not path.exists():
        return np.array([])
    return np.load(path, allow_pickle=False)


def load_profiles() -> pd.DataFrame:
    return load_parquet("profiles_clean.parquet")


def load_profile_vectors() -> pd.DataFrame:
    return load_parquet("profile_vectors.parquet")


def load_recommendations() -> pd.DataFrame:
    return load_parquet("recommendations.parquet")


def load_hotel_matrix() -> pd.DataFrame:
    return load_parquet("hotel_matrix.parquet")


def load_hotel_confidence_scores() -> pd.DataFrame:
    return load_parquet("hotel_confidence_scores.parquet")


def load_hotel_contradictions() -> pd.DataFrame:
    return load_parquet("hotel_contradictions.parquet")


def load_hotel_trends() -> pd.DataFrame:
    return load_parquet("hotel_trends.parquet")


def load_review_aspects() -> pd.DataFrame:
    return load_parquet("review_aspects.parquet")


def load_hotel_stats() -> pd.DataFrame:
    return load_parquet("hotel_stats.parquet")


def load_monthly_hotel_stats() -> pd.DataFrame:
    return load_parquet("monthly_hotel_stats.parquet")


def load_aspect_descriptions() -> dict[str, Any]:
    return load_json("aspect_descriptions.json")


def load_aspect_keywords() -> dict[str, Any]:
    return load_json("aspect_keywords.json")


def load_dataset_metadata() -> dict[str, Any]:
    return load_json("dataset_metadata.json")


def load_top_words() -> dict[str, Any]:
    return load_json("top_words.json")


def load_top_bigrams() -> dict[str, Any]:
    return load_json("top_bigrams.json")


def load_hotel_categories() -> dict[str, Any]:
    return load_json("hotel_categories.json")


def load_hotel_reviews() -> list[dict[str, Any]]:
    records = load_json("hotel_reviews.json")
    return records if isinstance(records, list) else []


def load_hotel_metadata() -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for review in load_hotel_reviews():
        hotel_id = str(review.get("hotel_id", "")).strip()
        if not hotel_id or hotel_id in metadata:
            continue
        metadata[hotel_id] = {
            "hotel_name": review.get("hotel_name", hotel_id),
            "hotel_category": review.get("hotel_category", "Unknown"),
        }
    return metadata


def numeric_aspect_columns(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    numeric_cols = [
        col
        for col in df.columns
        if col not in ID_COLUMNS and pd.api.types.is_numeric_dtype(df[col])
    ]
    ordered = [aspect for aspect in ASPECT_ORDER if aspect in numeric_cols]
    return ordered + [col for col in numeric_cols if col not in ordered]


def artifact_health() -> pd.DataFrame:
    expected = [
        "recommendations.parquet",
        "profile_vectors.parquet",
        "traveler_feature_store.parquet",
        "hotel_matrix.parquet",
        "hotel_feature_store.parquet",
        "hotel_confidence_scores.parquet",
        "hotel_contradictions.parquet",
        "hotel_trends.parquet",
        "consistency_matrix.parquet",
        "mention_matrix.parquet",
        "review_aspects.parquet",
        "hotel_reviews.json",
        "aspect_descriptions.json",
        "aspect_keywords.json",
        "aspect_embeddings.npy",
        "hotel_stats.parquet",
        "monthly_hotel_stats.parquet",
        "hotel_review_counts.json",
        "top_words.json",
        "top_bigrams.json",
        "dataset_metadata.json",
        "profiles_clean.parquet",
    ]
    rows = []
    for filename in expected:
        path = artifact_path(filename)
        rows.append(
            {
                "artifact": filename,
                "available": path.exists(),
                "size_mb": round(path.stat().st_size / 1_000_000, 2) if path.exists() else 0,
            }
        )
    return pd.DataFrame(rows)
