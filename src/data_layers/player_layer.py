"""Single-player data layer with identity, stats, and context."""

from src.data_layers.base import BaseDataLayer
from src.data_layers.colors import get_team_colors
from src.data_layers.context_engine import ContextEngine


class PlayerDataLayer(BaseDataLayer):
    """Fetches and structures all data needed for a single-player infographic."""

    # Columns to expose as 'key stats' for infographics
    KEY_STAT_COLUMNS = [
        "goals", "assists", "rating", "expected_goals",
        "shots_total", "shots_on_target", "shot_conversion_pct",
        "key_passes_p90", "pass_accuracy_pct",
        "tackles_p90", "interceptions_p90",
        "duels_aerial_pct", "dribbles_successful_p90",
        "big_chances", "xa", "progressive_carries_p90",
    ]

    def __init__(self, player_name: str, season_year: int, competition_id: int):
        super().__init__()
        self.player_name = player_name
        self.season_year = season_year
        self.competition_id = competition_id
        self.context_engine = ContextEngine(season_year, competition_id)

    def _fetch_identity(self) -> dict:
        """Player identity: name, team, position, colors."""
        self.execute(
            """
            SELECT
                p.id AS player_id,
                p.full_name,
                pos.name_es AS position,
                t.id AS team_id,
                t.name AS team_name,
                s.year,
                c.name AS competition_name
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            LEFT JOIN positions pos ON pos.id = p.position_id
            JOIN teams t ON t.id = pss.team_id
            JOIN seasons s ON s.id = pss.season_id
            JOIN competitions c ON c.id = s.competition_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
            LIMIT 1
            """,
            (self.player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        if not row:
            raise ValueError(f"Player '{self.player_name}' not found for {self.season_year} competition {self.competition_id}")

        keys = [
            "player_id", "full_name", "position", "team_id", "team_name",
            "year", "competition_name",
        ]
        result = dict(zip(keys, row))
        colors = get_team_colors(result["team_name"])
        result["primary_color"] = colors["primary"]
        result["secondary_color"] = colors["secondary"]
        return result

    def _fetch_basic_stats(self) -> dict:
        """Basic counting stats everyone understands."""
        self.execute(
            """
            SELECT
                matches_played,
                minutes_played,
                goals,
                assists,
                yellow_cards,
                red_cards
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN seasons s ON s.id = pss.season_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
            LIMIT 1
            """,
            (self.player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        keys = [
            "matches_played", "minutes_played", "goals", "assists",
            "yellow_cards", "red_cards",
        ]
        return dict(zip(keys, row))

    def _fetch_key_stats(self) -> dict:
        """Advanced stats for the main stats grid."""
        cols = ", ".join(self.KEY_STAT_COLUMNS)
        self.execute(
            f"""
            SELECT {cols}
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN seasons s ON s.id = pss.season_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
            LIMIT 1
            """,
            (self.player_name, self.season_year, self.competition_id),
        )
        row = self.fetchone()
        return dict(zip(self.KEY_STAT_COLUMNS, row))

    def _fetch_derived_stats(self, basic: dict, key: dict) -> dict:
        """Calculate derived stats that are easy to understand."""
        minutes = basic.get("minutes_played") or 0
        goals = basic.get("goals") or 0
        assists = basic.get("assists") or 0
        shots = key.get("shots_total") or 0
        shots_on = key.get("shots_on_target") or 0

        derived = {}

        if minutes > 0:
            derived["goals_per_90"] = round((goals / minutes) * 90, 2)
            derived["assists_per_90"] = round((assists / minutes) * 90, 2)
            derived["contributions_per_90"] = round(((goals + assists) / minutes) * 90, 2)
            derived["minutes_per_goal"] = round(minutes / goals, 1) if goals > 0 else None
        else:
            derived["goals_per_90"] = None
            derived["assists_per_90"] = None
            derived["contributions_per_90"] = None
            derived["minutes_per_goal"] = None

        if shots > 0:
            derived["shots_on_target_pct"] = round((shots_on / shots) * 100, 1)
        else:
            derived["shots_on_target_pct"] = None

        return derived

    def build_layers(self) -> dict:
        """Build all modular data layers for this player."""
        identity = self._fetch_identity()
        basic = self._fetch_basic_stats()
        key = self._fetch_key_stats()
        derived = self._fetch_derived_stats(basic, key)

        # Add context to key stats
        key_with_context = {}
        for col, val in key.items():
            if val is not None:
                key_with_context[col] = self.context_engine.get_context(col, val)

        # Add context to derived stats
        derived_meta = {
            "goals_per_90": ("Goles /90", "Goles cada 90 minutos de juego"),
            "assists_per_90": ("Asistencias /90", "Asistencias cada 90 minutos"),
            "contributions_per_90": ("G+A /90", "Goles + Asistencias cada 90 minutos"),
            "minutes_per_goal": ("Min/Gol", "Minutos necesarios para marcar un gol"),
            "shots_on_target_pct": ("Tiros al Arco (%)", "Porcentaje de tiros que van al arco"),
        }

        derived_with_context = {}
        for col, val in derived.items():
            if val is not None:
                label, desc = derived_meta.get(col, (col, ""))
                derived_with_context[col] = {
                    "value": val,
                    "label": label,
                    "description": desc,
                }

        return {
            "layer_identity": {
                "player_name": identity["full_name"],
                "player_id": identity["player_id"],
                "position": identity["position"],
                "team": identity["team_name"],
                "team_id": identity["team_id"],
                "team_colors": {
                    "primary": identity["primary_color"],
                    "secondary": identity["secondary_color"],
                },
                "season": identity["year"],
                "competition": identity["competition_name"],
            },
            "layer_basic_stats": {
                "matches": basic["matches_played"],
                "minutes": basic["minutes_played"],
                "goals": basic["goals"],
                "assists": basic["assists"],
                "yellow_cards": basic["yellow_cards"],
                "red_cards": basic["red_cards"],
            },
            "layer_key_stats": {
                col: {
                    "value": ctx.value,
                    "label": ctx.label,
                    "percentile": ctx.percentile,
                    "vs_average": ctx.vs_average,
                    "plain_text": ctx.plain_text,
                }
                for col, ctx in key_with_context.items()
            },
            "layer_derived_stats": derived_with_context,
            "layer_summary": {
                "headline": f"{identity['full_name']} - {identity['team_name']}",
                "subheadline": f"{identity['position'] or 'Jugador'} | {identity['competition_name']} {identity['year']}",
                "top_stat": {
                    "value": basic["goals"],
                    "label": "Goles",
                },
            },
        }
