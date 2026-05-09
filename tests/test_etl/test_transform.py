"""Tests for ETL transform module."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import pandas as pd
import pytest

from src.etl.transform import transform_players


class TestTransformPlayers:
    """Unit tests for transform_players."""

    def test_empty_dataframe_returns_empty(self):
        df = pd.DataFrame()
        result = transform_players(df, season_id=1)
        assert result.empty

    def test_column_mapping(self):
        df = pd.DataFrame({
            "player": ["Test Player"],
            "team": ["Test Team"],
            "minutesPlayed": [900],
            "goals": [5],
            "assists": [2],
            "rating": [7.5],
            "appearances": [10],
            "tackles": [20],
            "fouls": [10],
            "wasFouled": [15],
            "accurateCrosses": [8],
            "accurateLongBallsPercentage": [60.0],
            "offsides": [5],
            "hitWoodwork": [1],
            "blockedShots": [3],
            "dispossessed": [12],
            "dribbledPast": [8],
            "goalConversionPercentage": [25.0],
            "totalShots": [20],
            "shotsOnTarget": [10],
            "saves": [0],
            "accuratePassesPercentage": [85.0],
            "keyPasses": [25],
            "interceptions": [18],
            "clearances": [22],
            "accurateFinalThirdPasses": [40],
            "successfulDribblesPercentage": [55.0],
            "groundDuelsWonPercentage": [45.0],
            "aerialDuelsWonPercentage": [50.0],
        })
        result = transform_players(df, season_id=1)

        assert len(result) == 1
        row = result.iloc[0]
        assert row["player_name"] == "Test Player"
        assert row["team_name"] == "Test Team"
        assert row["goals"] == 5
        assert row["assists"] == 2
        assert row["minutes_played"] == 900
        assert row["matches_played"] == 10
        assert row["rating"] == 7.5
        assert row["tackles_p90"] == 20  # mapped directly, not computed
        assert row["fouls_committed_p90"] == 10
        assert row["fouls_won_p90"] == 15
        assert row["accurate_crosses_p90"] == 8
        assert row["long_pass_accuracy_pct"] == 60.0
        assert row["offsides_p90"] == 5
        assert row["hit_woodwork"] == 1
        assert row["shots_blocked"] == 3
        assert row["dispossessed_p90"] == 12
        assert row["dribbled_past_p90"] == 8
        assert row["shot_conversion_pct"] == 25.0
        assert row["shots_total"] == 20
        assert row["shots_on_target"] == 10
        assert row["saves_total"] == 0
        assert row["pass_accuracy_pct"] == 85.0
        assert row["key_passes_p90"] == 25
        assert row["interceptions_p90"] == 18
        assert row["clearances_p90"] == 22
        assert row["passes_final_third_p90"] == 40
        assert row["dribbles_successful_p90"] == 55.0
        assert row["duels_ground_won_p90"] == 45.0
        assert row["duels_aerial_pct"] == 50.0

    def test_season_id_and_source_injected(self):
        df = pd.DataFrame({
            "player": ["A"],
            "team": ["B"],
            "goals": [1],
        })
        result = transform_players(df, season_id=42, source="test")
        assert result.iloc[0]["season_id"] == 42
        assert result.iloc[0]["source"] == "test"

    def test_missing_columns_are_skipped(self):
        df = pd.DataFrame({
            "player": ["A"],
            "team": ["B"],
            "goals": [1],
        })
        result = transform_players(df, season_id=1)
        assert "assists" not in result.columns or pd.isna(result.iloc[0].get("assists"))

    def test_position_classification(self):
        df = pd.DataFrame({
            "player": ["A"],
            "team": ["B"],
            "goals": [1],
            "position_group": ["Forwards"],
        })
        result = transform_players(df, season_id=1)
        assert "position_id" in result.columns
