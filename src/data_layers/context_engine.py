"""Context engine: percentiles, league averages, plain-language descriptions."""

from dataclasses import dataclass
from typing import Any

from src.data_layers.base import BaseDataLayer


@dataclass(frozen=True)
class StatContext:
    """Contextual information for a single statistic."""

    value: float | int | None
    label: str
    abbreviation: str
    description: str
    percentile: int | None
    league_average: float | None
    vs_average: str | None
    plain_text: str | None
    is_good_high: bool


class ContextEngine(BaseDataLayer):
    """Calculates league context (percentiles, averages) to make stats understandable."""

    # Stats where higher is better
    HIGHER_IS_BETTER = {
        "goals", "assists", "rating", "shots_total", "shots_on_target",
        "key_passes_p90", "pass_accuracy_pct", "tackles_p90",
        "interceptions_p90", "duels_ground_won_p90", "duels_aerial_pct",
        "progressive_carries_p90", "passes_final_third_p90",
        "dribbles_successful_p90", "crosses_accurate_p90",
        "save_pct", "goals_prevented_xg", "expected_goals", "xa",
        "big_chances", "shot_conversion_pct", "accurate_crosses_p90",
        "fouls_won_p90",
    }

    # Human-readable labels and descriptions
    STAT_META = {
        "goals": ("Goles", "Goles marcados en la temporada"),
        "assists": ("Asistencias", "Pases que terminan en gol"),
        "rating": ("Calificación", "Calificación promedio SofaScore (1-10)"),
        "minutes_played": ("Minutos", "Minutos jugados en la temporada"),
        "matches_played": ("Partidos", "Partidos disputados"),
        "expected_goals": ("xG", "Goles esperados según calidad de tiros"),
        "shots_total": ("Tiros", "Total de tiros realizados"),
        "shots_on_target": ("Tiros al Arco", "Tiros que van entre los tres palos"),
        "key_passes_p90": ("Pases Clave /90", "Pases que generan ocasión de gol por cada 90 minutos"),
        "pass_accuracy_pct": ("Precisión de Pases (%)", "Porcentaje de pases completados"),
        "tackles_p90": ("Entradas /90", "Entradas exitosas por cada 90 minutos"),
        "interceptions_p90": ("Intercepciones /90", "Balones cortados por cada 90 minutos"),
        "shot_conversion_pct": ("Efectividad (%)", "Porcentaje de tiros que terminan en gol"),
        "duels_ground_won_p90": ("Duelos Ganados /90", "Duelos en el suelo ganados por 90 min"),
        "duels_aerial_pct": ("Duelos Aéreos (%)", "Porcentaje de duelos aéreos ganados"),
        "dribbles_successful_p90": ("Regates /90", "Regates exitosos por cada 90 minutos"),
        "big_chances": ("Ocasiones Claras", "Tiros con alta probabilidad de gol"),
        "xa": ("xA", "Asistencias esperadas"),
        "progressive_carries_p90": ("Conducciones Progresivas /90", "Conducciones hacia el área rival por 90 min"),
        "clearances_p90": ("Despejes /90", "Despejes por cada 90 minutos"),
        "fouls_won_p90": ("Faltas Recibidas /90", "Faltas a favor por cada 90 minutos"),
        "yellow_cards": ("Amarillas", "Tarjetas amarillas recibidas"),
        "red_cards": ("Rojas", "Tarjetas rojas recibidas"),
    }

    def __init__(self, season_year: int, competition_id: int, min_minutes: int = 270):
        super().__init__()
        self.season_year = season_year
        self.competition_id = competition_id
        self.min_minutes = min_minutes

    def _get_league_values(self, column: str) -> list[float]:
        """Fetch all non-null values for a stat across the league."""
        self.execute(
            f"""
            SELECT {column}
            FROM player_season_stats pss
            JOIN seasons s ON s.id = pss.season_id
            WHERE s.year = %s AND s.competition_id = %s
              AND pss.minutes_played >= %s
              AND {column} IS NOT NULL
            """,
            (self.season_year, self.competition_id, self.min_minutes),
        )
        return [row[0] for row in self.fetchall() if row[0] is not None]

    def _percentile(self, value: float, values: list[float], higher_is_better: bool) -> int:
        """Calculate percentile rank (0-100)."""
        if not values:
            return 50
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        # Find rank
        if higher_is_better:
            rank = sum(1 for v in values if v <= value)
        else:
            rank = sum(1 for v in values if v >= value)
        return int((rank / n) * 100)

    def _plain_text(self, label: str, percentile: int | None, value: float, avg: float | None, column: str) -> str:
        """Generate a one-sentence plain-language summary."""
        if percentile is None:
            return None

        # Tier descriptions
        if percentile >= 95:
            tier = "Elite"
        elif percentile >= 85:
            tier = "Destacado"
        elif percentile >= 70:
            tier = "Por Encima del Promedio"
        elif percentile >= 40:
            tier = "Promedio"
        else:
            tier = "Por Debajo del Promedio"

        # Specific plain text based on stat
        if column == "goals":
            return f"{tier} - Goleador de alto nivel" if percentile >= 90 else f"{tier}"
        elif column == "rating":
            return f"{tier} - Rendimiento excepcional" if percentile >= 90 else f"{tier}"
        elif column == "expected_goals":
            return f"{tier} - Genera muchas ocasiones de gol" if percentile >= 85 else f"{tier}"
        elif column == "shot_conversion_pct":
            return f"{tier} - Muy clínico definiendo" if percentile >= 85 else f"{tier}"
        elif column == "pass_accuracy_pct":
            return f"{tier} - Excelente distribución" if percentile >= 85 else f"{tier}"
        elif column == "key_passes_p90":
            return f"{tier} - Creador de juego peligroso" if percentile >= 85 else f"{tier}"
        elif column == "tackles_p90" or column == "interceptions_p90":
            return f"{tier} - Intenso en la recuperación" if percentile >= 85 else f"{tier}"
        elif column == "duels_aerial_pct":
            return f"{tier} - Dominador en el juego aéreo" if percentile >= 85 else f"{tier}"
        elif column == "dribbles_successful_p90":
            return f"{tier} - Desequilibrante con balón" if percentile >= 85 else f"{tier}"

        return tier

    def get_context(self, column: str, value: float | None) -> StatContext:
        """Get full context for a single statistic."""
        label, description = self.STAT_META.get(column, (column.replace("_", " ").title(), ""))
        abbreviation = label

        if value is None:
            return StatContext(
                value=None,
                label=label,
                abbreviation=abbreviation,
                description=description,
                percentile=None,
                league_average=None,
                vs_average=None,
                plain_text=None,
                is_good_high=column in self.HIGHER_IS_BETTER,
            )

        values = self._get_league_values(column)
        is_good_high = column in self.HIGHER_IS_BETTER
        percentile = self._percentile(value, values, is_good_high) if values else None
        league_average = sum(values) / len(values) if values else None

        vs_average = None
        if league_average is not None and league_average > 0:
            diff_pct = ((value - league_average) / league_average) * 100
            if diff_pct > 0:
                vs_average = f"+{diff_pct:.0f}% vs promedio"
            elif diff_pct < 0:
                vs_average = f"{diff_pct:.0f}% vs promedio"
            else:
                vs_average = "Promedio"

        plain = self._plain_text(label, percentile, value, league_average, column)

        return StatContext(
            value=value,
            label=label,
            abbreviation=abbreviation,
            description=description,
            percentile=percentile,
            league_average=round(league_average, 2) if league_average else None,
            vs_average=vs_average,
            plain_text=plain,
            is_good_high=is_good_high,
        )

    def get_all_contexts(self, stats_dict: dict[str, Any]) -> dict[str, StatContext]:
        """Get context for a dictionary of stats."""
        return {col: self.get_context(col, val) for col, val in stats_dict.items()}
