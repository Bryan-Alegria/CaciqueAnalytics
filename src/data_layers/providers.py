"""League stats provider interface and implementations."""

from typing import Protocol

from src.data_layers.base import BaseDataLayer


class LeagueStatsProvider(Protocol):
    """Protocol for fetching league-wide stat distributions."""

    def get_values(self, column: str, season_year: int, competition_id: int, min_minutes: int) -> list[float]:
        """Return all non-null values for a stat across the league."""
        ...


class DbLeagueStatsProvider:
    """Database-backed provider using BaseDataLayer."""

    def __init__(self):
        self._layer = BaseDataLayer()

    def get_values(self, column: str, season_year: int, competition_id: int, min_minutes: int) -> list[float]:
        self._layer.execute(
            f"""
            SELECT {column}
            FROM player_season_stats pss
            JOIN seasons s ON s.id = pss.season_id
            WHERE s.year = %s AND s.competition_id = %s
              AND pss.minutes_played >= %s
              AND {column} IS NOT NULL
            """,
            (season_year, competition_id, min_minutes),
        )
        return [row[0] for row in self._layer.fetchall() if row[0] is not None]

    def close(self) -> None:
        self._layer.close()
