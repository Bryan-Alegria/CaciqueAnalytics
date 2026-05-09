"""Tests for xG calculation module."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline


class TestXGModel:
    """Unit tests for the xG prediction model logic."""

    def test_model_can_train_on_sample_data(self):
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import StandardScaler

        df = pd.DataFrame({
            "xg": [0.5, 1.2, 0.3, 2.1, 0.8],
            "shots_total": [10, 25, 5, 40, 15],
            "shots_on_target": [4, 12, 2, 18, 7],
            "goals": [1, 3, 0, 5, 2],
            "big_chances_missed": [2, 1, 0, 3, 1],
            "shot_conversion_pct": [10.0, 12.0, 0.0, 12.5, 13.3],
            "minutes_played": [900, 1800, 450, 2700, 1350],
            "rating": [6.5, 7.2, 6.0, 7.8, 7.0],
            "assists": [0, 2, 1, 3, 1],
            "key_passes_p90": [1.5, 2.3, 0.8, 3.1, 1.9],
            "tackles_p90": [1.2, 0.8, 2.1, 0.5, 1.5],
            "pass_accuracy_pct": [75.0, 82.0, 68.0, 85.0, 78.0],
        })

        feature_cols = [
            "shots_total", "shots_on_target", "goals", "big_chances_missed",
            "shot_conversion_pct", "minutes_played", "rating", "assists",
            "key_passes_p90", "tackles_p90", "pass_accuracy_pct"
        ]

        pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=10, random_state=42))
        ])

        pipeline.fit(df[feature_cols], df["xg"])
        preds = pipeline.predict(df[feature_cols])

        assert len(preds) == 5
        assert all(preds >= 0)  # No negative xG

    def test_prediction_for_zero_shots(self):
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import StandardScaler

        df = pd.DataFrame({
            "xg": [0.0, 0.1, 0.0],
            "shots_total": [0, 1, 0],
            "shots_on_target": [0, 0, 0],
            "goals": [0, 0, 0],
            "big_chances_missed": [0, 0, 1],
            "shot_conversion_pct": [0.0, 0.0, 0.0],
            "minutes_played": [90, 45, 180],
            "rating": [6.0, 6.1, 6.2],
            "assists": [0, 0, 0],
            "key_passes_p90": [0.0, 0.0, 0.0],
            "tackles_p90": [1.0, 1.0, 1.0],
            "pass_accuracy_pct": [70.0, 70.0, 70.0],
        })

        feature_cols = list(df.columns)[1:]

        pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=10, random_state=42))
        ])

        pipeline.fit(df[feature_cols], df["xg"])
        pred = pipeline.predict(pd.DataFrame([{
            "shots_total": 0, "shots_on_target": 0, "goals": 0,
            "big_chances_missed": 0, "shot_conversion_pct": 0.0,
            "minutes_played": 90, "rating": 6.0, "assists": 0,
            "key_passes_p90": 0.0, "tackles_p90": 1.0, "pass_accuracy_pct": 70.0
        }]))

        assert pred[0] >= 0  # Should not be negative even with 0 shots

    def test_feature_importance_ordering(self):
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import StandardScaler

        df = pd.DataFrame({
            "xg": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.2, 1.8, 0.9, 1.1],
            "shots_total": [10, 25, 5, 40, 15, 30, 3, 35, 18, 22],
            "shots_on_target": [4, 12, 2, 18, 7, 14, 1, 16, 8, 10],
            "goals": [1, 3, 0, 5, 2, 4, 0, 4, 2, 3],
            "big_chances_missed": [2, 1, 0, 3, 1, 2, 0, 2, 1, 1],
            "shot_conversion_pct": [10.0, 12.0, 0.0, 12.5, 13.3, 13.3, 0.0, 11.4, 11.1, 13.6],
            "minutes_played": [900, 1800, 450, 2700, 1350, 2250, 180, 2500, 1600, 1900],
            "rating": [6.5, 7.2, 6.0, 7.8, 7.0, 7.5, 5.8, 7.6, 7.1, 7.3],
            "assists": [0, 2, 1, 3, 1, 2, 0, 3, 1, 2],
            "key_passes_p90": [1.5, 2.3, 0.8, 3.1, 1.9, 2.5, 0.5, 2.9, 2.0, 2.2],
            "tackles_p90": [1.2, 0.8, 2.1, 0.5, 1.5, 0.9, 2.5, 0.6, 1.3, 1.0],
            "pass_accuracy_pct": [75.0, 82.0, 68.0, 85.0, 78.0, 80.0, 65.0, 83.0, 79.0, 81.0],
        })

        feature_cols = list(df.columns)[1:]

        pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=50, random_state=42))
        ])

        pipeline.fit(df[feature_cols], df["xg"])
        importances = pipeline.named_steps["model"].feature_importances_

        # shots_on_target or shots_total should be top features
        top_feature_idx = np.argmax(importances)
        top_feature = feature_cols[top_feature_idx]
        assert top_feature in ["shots_total", "shots_on_target", "goals"]
