"""SofaScore API client wrapping LanusStats with logging and clean output."""

import logging
from typing import Optional

import pandas as pd

import LanusStats as ls

logger = logging.getLogger(__name__)


class SofaScoreClient:
    """Wrapper around LanusStats SofaScore module."""

    POSITION_GROUPS = ["Goalkeepers", "Defenders", "Midfielders", "Forwards"]

    def __init__(self):
        self.client = ls.SofaScore()
        logger.info("SofaScoreClient initialized")

    def get_seasons(self, league_name: str) -> dict:
        """Return available seasons for a league."""
        return ls.get_available_season_for_leagues("Sofascore", league_name)

    def scrape_players(
        self,
        league: str,
        season: str,
        accumulation: str = "total",
        position_group: Optional[str] = None,
    ) -> pd.DataFrame:
        """Scrape player stats for a league/season.

        Args:
            league: League name (e.g. 'Chile Primera Division')
            season: Season year (e.g. '2026')
            accumulation: 'total', 'per90', or 'perMatch'
            position_group: 'Goalkeepers', 'Defenders', 'Midfielders', 'Forwards'

        Returns:
            DataFrame with player stats
        """
        positions = [position_group] if position_group else self.POSITION_GROUPS
        frames = []

        for pos in positions:
            logger.info(f"Scraping {pos} for {league} {season}")
            try:
                df = self.client.scrape_league_stats(
                    league=league,
                    season=season,
                    accumulation=accumulation,
                    selected_positions=[pos],
                )
                df["position_group"] = pos
                frames.append(df)
                logger.info(f"  -> {len(df)} rows")
            except Exception as e:
                logger.error(f"  -> Failed: {e}")
                raise

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def scrape_all_positions(
        self, league: str, season: str, accumulation: str = "total"
    ) -> pd.DataFrame:
        """Scrape all position groups and return combined DataFrame."""
        return self.scrape_players(league, season, accumulation)

    def get_tournament_table(self, url: str) -> pd.DataFrame:
        """Scrape league standings from FBRef-style URL (fallback)."""
        # TODO: Implement direct standings scraping
        return pd.DataFrame()
