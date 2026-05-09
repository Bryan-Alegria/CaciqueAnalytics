"""Extract data from SofaScore API."""

import logging
from typing import Optional

import pandas as pd

from src.scraper.sofascore_client import SofaScoreClient

logger = logging.getLogger(__name__)


def extract_players(
    league: str,
    season: str,
    position_group: Optional[str] = None,
    accumulation: str = "total",
) -> pd.DataFrame:
    """Extract player season stats from SofaScore.

    Args:
        league: League name (e.g. 'Chile Primera Division')
        season: Season year (e.g. '2026')
        position_group: Filter by position group, or None for all
        accumulation: 'total', 'per90', or 'perMatch'

    Returns:
        Raw DataFrame from SofaScore
    """
    client = SofaScoreClient()
    df = client.scrape_players(league, season, accumulation, position_group)
    logger.info(f"Extracted {len(df)} player records from {league} {season}")
    return df
