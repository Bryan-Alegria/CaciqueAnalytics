"""ETL orchestrator. Runs full pipeline for a competition."""

import logging
from datetime import datetime

from src.etl.extract import extract_players
from src.etl.load import load_players
from src.etl.transform import transform_players

logger = logging.getLogger(__name__)


def run_pipeline(
    league: str,
    season: str,
    season_id: int,
    competition_id: int,
    accumulation: str = "total",
):
    """Run full ETL pipeline for a league/season.

    Args:
        league: League name for scraping (e.g. 'Chile Primera Division')
        season: Season year string (e.g. '2026')
        season_id: Database season_id
        competition_id: Database competition_id
        accumulation: 'total', 'per90', or 'perMatch'
    """
    logger.info(f"Starting ETL: {league} {season} (season_id={season_id})")

    # Extract
    raw_df = extract_players(league, season, accumulation=accumulation)

    # Transform
    clean_df = transform_players(raw_df, season_id)

    # Load
    stats = load_players(clean_df, season_id, competition_id)

    logger.info(f"ETL complete: {stats}")
    return stats


def run_chile_primera_2026():
    """Convenience function for Chilean Primera Division 2026."""
    return run_pipeline(
        league="Chile Primera Division",
        season="2026",
        season_id=1,  # TODO: fetch from DB
        competition_id=1,
    )
