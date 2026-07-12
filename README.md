# Hotel Review Intelligence Engine

Explainable hotel intelligence app for the Expedia hackathon.

The notebooks in `notebooks/` already produced the ML outputs. This repository only ships the Streamlit app and consumes the generated files in `artifacts/`; it does not retrain models or regenerate artifacts.

## What you need

1. Python 3.10 or newer.
2. The repository clone.
3. The checked-in `artifacts/` directory.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

On macOS or Linux, activate the virtual environment with `source .venv/bin/activate`.

## Pages

- `Profile Explorer`: traveler descriptions, top priorities, radar charts, and aspect importance.
- `Hotel Recommendations`: top 5 recommendations per profile with match score, reasons, strengths, warnings, and trend.
- `System Insights`: aspect distribution, review volume, hotel stats, temporal trends, and contradiction examples.

## Deployment

The app is ready for Streamlit Cloud.

- Entry point: `app/streamlit_app.py`
- Dependencies: `requirements.txt`
- Streamlit config: `.streamlit/config.toml`

## Artifact Contract

The app reads schemas directly from the existing artifacts and handles missing fields with empty states instead of synthetic data.

Primary files used:

- `artifacts/recommendations.parquet`
- `artifacts/hotel_reviews.json`
- `artifacts/profile_vectors.parquet`
- `artifacts/profiles_clean.parquet`
- `artifacts/hotel_matrix.parquet`
- `artifacts/hotel_contradictions.parquet`
- `artifacts/hotel_trends.parquet`
- `artifacts/review_aspects.parquet`
- `artifacts/hotel_stats.parquet`
- `artifacts/monthly_hotel_stats.parquet`
- `artifacts/dataset_metadata.json`
- `artifacts/top_words.json`
- `artifacts/top_bigrams.json`
