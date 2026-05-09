"""Leaderboard / top lists data layer."""

from src.data_layers.base import BaseDataLayer


class LeaderboardDataLayer(BaseDataLayer):
    """Generates ranked leaderboards for infographics."""

    def __init__(self, season_year: int, competition_id: int, min_minutes: int = 270):
        super().__init__()
        self.season_year = season_year
        self.competition_id = competition_id
        self.min_minutes = min_minutes

    def _fetch_top(self, column: str, label: str, limit: int = 5, fmt: str = "{}") -> list[dict]:
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

        results = []
        for rank, row in enumerate(self.fetchall(), start=1):
            name, team, val, matches, minutes = row
            results.append({
                "rank": rank,
                "player_name": name,
                "team": team,
                "value": val,
                "display_value": fmt.format(val),
                "matches": matches,
                "minutes": minutes,
            })
        return results

    def build_layers(self) -> dict:
        """Build all leaderboard layers."""
        return {
            "layer_identity": {
                "season": self.season_year,
                "competition_id": self.competition_id,
                "min_minutes": self.min_minutes,
            },
            "layer_top_scorers": self._fetch_top("goals", "Goles", 5, "{}"),
            "layer_top_assists": self._fetch_top("assists", "Asistencias", 5, "{}"),
            "layer_top_rating": self._fetch_top("rating", "Calificación", 5, "{:.2f}"),
            "layer_top_xg": self._fetch_top("expected_goals", "xG", 5, "{:.2f}"),
            "layer_top_shots": self._fetch_top("shots_total", "Tiros", 5, "{}"),
            "layer_top_key_passes": self._fetch_top("key_passes_p90", "Pases Clave /90", 5, "{:.2f}"),
            "layer_top_tackles": self._fetch_top("tackles_p90", "Entradas /90", 5, "{:.2f}"),
        }
