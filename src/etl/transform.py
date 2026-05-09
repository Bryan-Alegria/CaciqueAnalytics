"""Transform raw SofaScore data into DB-ready format."""

import logging
from typing import Optional

import pandas as pd

from src.scraper.position_classifier import classify_position

logger = logging.getLogger(__name__)

# Column mapping: SofaScore -> DB
COLUMN_MAP = {
    "goals": "goals",
    "yellowCards": "yellow_cards",
    "redCards": "red_cards",
    "groundDuelsWon": None,  # needs per90
    "groundDuelsWonPercentage": "duels_ground_won_p90",  # stored as percentage
    "aerialDuelsWon": None,
    "aerialDuelsWonPercentage": "duels_aerial_pct",
    "successfulDribbles": None,
    "successfulDribblesPercentage": "dribbles_successful_p90",
    "tackles": "tackles_p90",
    "assists": "assists",
    "accuratePassesPercentage": "pass_accuracy_pct",
    "totalDuelsWon": None,
    "totalDuelsWonPercentage": None,
    "minutesPlayed": "minutes_played",
    "wasFouled": "fouls_won_p90",
    "fouls": "fouls_committed_p90",
    "dispossessed": "dispossessed_p90",
    "appearances": "matches_played",
    "saves": "saves_total",
    "savedShotsFromInsideTheBox": None,
    "savedShotsFromOutsideTheBox": None,
    "goalsConcededInsideTheBox": None,
    "goalsConcededOutsideTheBox": None,
    "highClaims": None,
    "successfulRunsOut": None,
    "punches": None,
    "runsOut": None,
    "accurateFinalThirdPasses": "passes_final_third_p90",
    "bigChancesCreated": None,
    "accuratePasses": None,
    "keyPasses": "key_passes_p90",
    "accurateCrosses": "accurate_crosses_p90",
    "accurateCrossesPercentage": None,
    "accurateLongBalls": None,
    "accurateLongBallsPercentage": "long_pass_accuracy_pct",
    "interceptions": "interceptions_p90",
    "clearances": "clearances_p90",
    "dribbledPast": "dribbled_past_p90",
    "bigChancesMissed": "big_chances_missed",
    "totalShots": "shots_total",
    "shotsOnTarget": "shots_on_target",
    "blockedShots": "shots_blocked",
    "goalConversionPercentage": "shot_conversion_pct",
    "hitWoodwork": "hit_woodwork",
    "offsides": "offsides_p90",
    "expectedGoals": "expected_goals",
    "errorLeadToGoal": None,
    "errorLeadToShot": None,
    "passToAssist": None,
    "rating": "rating",
    "player": "player_name",
    "team": "team_name",
}


def transform_players(
    df: pd.DataFrame, season_id: int, source: str = "sofascore"
) -> pd.DataFrame:
    """Transform raw SofaScore DataFrame into DB-ready format.

    Args:
        df: Raw DataFrame from extract step
        season_id: Database season_id
        source: Data source identifier

    Returns:
        Clean DataFrame ready for load step
    """
    if df.empty:
        return df

    records = []
    for _, row in df.iterrows():
        record = {"season_id": season_id, "source": source}

        # Map known columns
        for ss_col, db_col in COLUMN_MAP.items():
            if db_col and ss_col in row:
                record[db_col] = row[ss_col]

        # Position classification
        record["position_id"] = classify_position(
            row.get("player", ""),
            row.get("position_group", ""),
            row.get("team", ""),
        )

        records.append(record)

    result = pd.DataFrame(records)
    logger.info(f"Transformed {len(result)} records")
    return result
