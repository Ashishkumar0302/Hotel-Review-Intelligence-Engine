# Hotel Review Intelligence Engine

Production Streamlit application for exploring Expedia-style hotel recommendations from existing pipeline artifacts.

The machine learning pipeline is complete and lives in the notebooks under `notebooks/`. The app only consumes generated files in `artifacts/`; it does not retrain models, regenerate outputs, or modify recommendation logic.

## App Pages

- `Profile Explorer`: traveler profile descriptions, top aspect priorities, radar charts, and importance bars.
- `Hotel Recommendations`: top 5 recommendations per profile with relevance score, match reasons, strengths, confidence, trend, and contradiction warnings.
- `System Insights`: aspect distribution, review volume, hotel statistics, language signals, temporal trends, and contradiction examples.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Streamlit Cloud

Use `app/streamlit_app.py` as the entry point. The repository includes `requirements.txt` and `.streamlit/config.toml` for deployment.

## Artifact Contract

The app reads schemas directly from the existing artifacts and handles missing fields with empty states instead of synthetic data.

Primary files used:

- `artifacts/recommendations.parquet`
- `artifacts/profile_vectors.parquet`
- `artifacts/profiles_clean.parquet`
- `artifacts/hotel_matrix.parquet`
- `artifacts/hotel_confidence_scores.parquet`
- `artifacts/hotel_contradictions.parquet`
- `artifacts/hotel_trends.parquet`
- `artifacts/review_aspects.parquet`
- `artifacts/hotel_stats.parquet`
- `artifacts/monthly_hotel_stats.parquet`
- `artifacts/dataset_metadata.json`
- `artifacts/top_words.json`
- `artifacts/top_bigrams.json`
