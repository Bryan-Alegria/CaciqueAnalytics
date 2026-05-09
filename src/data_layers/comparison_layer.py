"""Head-to-head player comparison data layer."""

from src.data_layers.base import BaseDataLayer
from src.data_layers.colors import get_team_colors
from src.data_layers.context_engine import ContextEngine
from src.data_layers import stat_registry
from src.data_layers import queries


class ComparisonDataLayer(BaseDataLayer):
    """Generates side-by-side comparison data for two players."""

    def __init__(self, player1_name: str, player2_name: str, season_year: int, competition_id: int):
        super().__init__()
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.season_year = season_year
        self.competition_id = competition_id
        self.context_engine = ContextEngine(season_year, competition_id)

    def _fetch_player_stats(self, player_name: str) -> dict:
        """Fetch raw stats for a player."""
        cols = stat_registry.comparison_stats() + ["matches_played", "minutes_played"]
        self.execute(
            queries.player_season_base(cols),
            (player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        if not row:
            raise ValueError(f"Player '{player_name}' not found")
        return dict(zip(cols, row))

    def _fetch_identity(self, player_name: str) -> dict:
        """Fetch identity info."""
        self.execute(
            queries.player_identity_base(),
            (player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        keys = ["player_id", "name", "position", "team_id", "team", "year", "competition_name"]
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
            "is_higher_better": stat_registry.higher_is_better(stat_key),
        }

    def close(self) -> None:
        self.context_engine.close()
        super().close()

    def build_layers(self) -> dict:
        """Build H2H comparison layers."""
        p1_stats = self._fetch_player_stats(self.player1_name)
        p2_stats = self._fetch_player_stats(self.player2_name)
        p1_id = self._fetch_identity(self.player1_name)
        p2_id = self._fetch_identity(self.player2_name)

        categories = []
        for stat_def in stat_registry.comparison_stats():
            meta = stat_registry.get(stat_def)
            categories.append(self._build_category(
                meta.label, meta.column,
                p1_stats.get(meta.column), p2_stats.get(meta.column),
                meta.fmt
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
