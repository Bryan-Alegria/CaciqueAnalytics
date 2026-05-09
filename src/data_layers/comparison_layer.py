"""Head-to-head player comparison data layer."""

from src.data_layers.base import BaseDataLayer
from src.data_layers.colors import get_team_colors
from src.data_layers.context_engine import ContextEngine
from src.data_layers.player_layer import PlayerDataLayer


class ComparisonDataLayer(BaseDataLayer):
    """Generates side-by-side comparison data for two players."""

    COMPARISON_STATS = [
        "goals", "assists", "rating", "expected_goals",
        "shots_total", "shots_on_target", "shot_conversion_pct",
        "key_passes_p90", "pass_accuracy_pct",
        "tackles_p90", "interceptions_p90",
        "duels_aerial_pct", "dribbles_successful_p90",
        "big_chances", "xa",
    ]

    def __init__(self, player1_name: str, player2_name: str, season_year: int, competition_id: int):
        super().__init__()
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.season_year = season_year
        self.competition_id = competition_id
        self.context_engine = ContextEngine(season_year, competition_id)

    def _fetch_player_stats(self, player_name: str) -> dict:
        """Fetch raw stats for a player."""
        cols = ", ".join(self.COMPARISON_STATS)
        self.execute(
            f"""
            SELECT {cols}, matches_played, minutes_played
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN seasons s ON s.id = pss.season_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
            LIMIT 1
            """,
            (player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        if not row:
            raise ValueError(f"Player '{player_name}' not found")

        all_cols = self.COMPARISON_STATS + ["matches_played", "minutes_played"]
        return dict(zip(all_cols, row))

    def _fetch_identity(self, player_name: str) -> dict:
        """Fetch identity info."""
        self.execute(
            """
            SELECT p.full_name, pos.name_es AS position, t.name
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            LEFT JOIN positions pos ON pos.id = p.position_id
            JOIN teams t ON t.id = pss.team_id
            JOIN seasons s ON s.id = pss.season_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            LIMIT 1
            """,
            (player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        keys = ["name", "position", "team"]
        result = dict(zip(keys, row))
        colors = get_team_colors(result["team"])
        result["primary_color"] = colors["primary"]
        result["secondary_color"] = colors["secondary"]
        return result

    def _build_category(self, label: str, stat_key: str, p1_val, p2_val, fmt: str = "{}") -> dict:
        """Build a comparison category with winner."""
        if p1_val is None or p2_val is None:
            winner = None
        elif p1_val > p2_val:
            winner = "player1"
        elif p2_val > p1_val:
            winner = "player2"
        else:
            winner = "tie"

        diff = None
        if p1_val is not None and p2_val is not None:
            diff = round(p1_val - p2_val, 2)

        return {
            "label": label,
            "stat_key": stat_key,
            "player1_value": p1_val,
            "player2_value": p2_val,
            "player1_display": fmt.format(p1_val) if p1_val is not None else "N/A",
            "player2_display": fmt.format(p2_val) if p2_val is not None else "N/A",
            "winner": winner,
            "difference": diff,
            "is_higher_better": stat_key in ContextEngine.HIGHER_IS_BETTER,
        }

    def build_layers(self) -> dict:
        """Build H2H comparison layers."""
        p1_stats = self._fetch_player_stats(self.player1_name)
        p2_stats = self._fetch_player_stats(self.player2_name)
        p1_id = self._fetch_identity(self.player1_name)
        p2_id = self._fetch_identity(self.player2_name)

        categories = []
        category_map = {
            "goals": ("Goles", "{}"),
            "assists": ("Asistencias", "{}"),
            "rating": ("Rating", "{:.2f}"),
            "expected_goals": ("xG", "{:.2f}"),
            "shots_total": ("Tiros", "{}"),
            "shots_on_target": ("Tiros al Arco", "{}"),
            "shot_conversion_pct": ("Efectividad (%)", "{:.1f}%"),
            "key_passes_p90": ("Pases Clave /90", "{:.2f}"),
            "pass_accuracy_pct": ("Precisión Pases (%)", "{:.1f}%"),
            "tackles_p90": ("Entradas /90", "{:.2f}"),
            "interceptions_p90": ("Intercepciones /90", "{:.2f}"),
            "duels_aerial_pct": ("Duelos Aéreos (%)", "{:.1f}%"),
            "dribbles_successful_p90": ("Regates /90", "{:.2f}"),
            "big_chances": ("Ocasiones Claras", "{}"),
            "xa": ("xA", "{:.2f}"),
        }

        for stat_key, (label, fmt) in category_map.items():
            categories.append(self._build_category(
                label, stat_key,
                p1_stats.get(stat_key), p2_stats.get(stat_key),
                fmt
            ))

        # Count wins
        p1_wins = sum(1 for c in categories if c["winner"] == "player1")
        p2_wins = sum(1 for c in categories if c["winner"] == "player2")
        ties = sum(1 for c in categories if c["winner"] == "tie")

        return {
            "layer_identity": {
                "player1": {
                    "name": p1_id["name"],
                    "position": p1_id["position"] or "Jugador",
                    "team": p1_id["team"],
                    "colors": {
                        "primary": p1_id["primary_color"],
                        "secondary": p1_id["secondary_color"],
                    },
                },
                "player2": {
                    "name": p2_id["name"],
                    "position": p2_id["position"] or "Jugador",
                    "team": p2_id["team"],
                    "colors": {
                        "primary": p2_id["primary_color"],
                        "secondary": p2_id["secondary_color"],
                    },
                },
                "season": self.season_year,
                "competition_id": self.competition_id,
            },
            "layer_summary": {
                "headline": f"{p1_id['name']} vs {p2_id['name']}",
                "subheadline": f"{p1_id['team']} vs {p2_id['team']} | {self.season_year}",
                "score": {
                    "player1_wins": p1_wins,
                    "player2_wins": p2_wins,
                    "ties": ties,
                },
            },
            "layer_categories": categories,
            "layer_basic_stats": {
                "player1": {
                    "matches": p1_stats["matches_played"],
                    "minutes": p1_stats["minutes_played"],
                },
                "player2": {
                    "matches": p2_stats["matches_played"],
                    "minutes": p2_stats["minutes_played"],
                },
            },
        }
