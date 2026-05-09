"""Leaderboard / top lists data layer."""

from src.data_layers.base import BaseDataLayer
from src.data_layers import stat_registry


class LeaderboardDataLayer(BaseDataLayer):
    """Generates ranked leaderboards for infographics."""

    def __init__(self, season_year: int, competition_id: int, min_minutes: int = 270):
        super().__init__()
        self.season_year = season_year
        self.competition_id = competition_id
        self.min_minutes = min_minutes

    def _fetch_top(self, column: str, limit: int = 5) -> list[dict]:
        """Fetch top N players for a given stat."""
        self.execute(
            f"""
            SELECT
                p.full_name,
                t.name AS team_name,
                pss.{column},
                pss.matches_played,
                pss.minutes_played
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN teams t ON t.id = pss.team_id
            JOIN seasons s ON s.id = pss.season_id
            WHERE s.year = %s AND s.competition_id = %s
              AND pss.minutes_played >= %s
              AND pss.{column} IS NOT NULL
            ORDER BY pss.{column} DESC
            LIMIT %s
            """,
            (self.season_year, self.competition_id, self.min_minutes, limit),
        )

        meta = stat_registry.get(column)
        results = []
        for rank, row in enumerate(self.fetchall(), start=1):
            name, team, val, matches, minutes = row
            results.append({
                "rank": rank,
                "player_name": name,
                "team": team,
                "value": val,
                "display_value": meta.leaderboard_format.format(val),
                "matches": matches,
                "minutes": minutes,
            })
        return results

    def build_layers(self) -> dict:
        """Build all leaderboard layers."""
        layers = {
            "layer_identity": {
                "season": self.season_year,
                "competition_id": self.competition_id,
                "min_minutes": self.min_minutes,
            },
        }
        for stat_def in stat_registry.leaderboard_stats():
            layer_name = f"layer_top_{stat_def.column}"
            layers[layer_name] = self._fetch_top(stat_def.column, 5)
        return layers
