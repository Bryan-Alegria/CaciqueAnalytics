"""Central registry for all player statistics metadata."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class StatDefinition:
    """Full metadata for a single player statistic."""

    column: str
    label: str
    description: str
    fmt: str
    higher_is_better: bool = True
    plain_text_rules: list[tuple[int, str]] | None = None
    is_key_stat: bool = True
    is_comparison_stat: bool = True
    is_leaderboard_stat: bool = False
    leaderboard_fmt: str | None = None

    @property
    def leaderboard_format(self) -> str:
        return self.leaderboard_fmt or self.fmt


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_GOAL_RULES = [(90, "Elite - Goleador de alto nivel")]
_RATING_RULES = [(90, "Elite - Rendimiento excepcional")]
_XG_RULES = [(85, "Destacado - Genera muchas ocasiones de gol")]
_CONVERSION_RULES = [(85, "Destacado - Muy clinico definiendo")]
_PASS_RULES = [(85, "Destacado - Excelente distribucion")]
_KEY_PASS_RULES = [(85, "Destacado - Creador de juego peligroso")]
_TACKLE_RULES = [(85, "Destacado - Intenso en la recuperacion")]
_AERIAL_RULES = [(85, "Destacado - Dominador en el juego aereo")]
_DRIBBLE_RULES = [(85, "Destacado - Desequilibrante con balon")]

_REGISTRY: dict[str, StatDefinition] = {
    "goals": StatDefinition(
        column="goals",
        label="Goles",
        description="Goles marcados en la temporada",
        fmt="{}",
        plain_text_rules=_GOAL_RULES,
        is_leaderboard_stat=True,
    ),
    "assists": StatDefinition(
        column="assists",
        label="Asistencias",
        description="Pases que terminan en gol",
        fmt="{}",
        is_leaderboard_stat=True,
    ),
    "rating": StatDefinition(
        column="rating",
        label="Calificacion",
        description="Calificacion promedio SofaScore (1-10)",
        fmt="{:.2f}",
        plain_text_rules=_RATING_RULES,
        is_leaderboard_stat=True,
    ),
    "minutes_played": StatDefinition(
        column="minutes_played",
        label="Minutos",
        description="Minutos jugados en la temporada",
        fmt="{}",
        is_key_stat=False,
        is_comparison_stat=False,
    ),
    "matches_played": StatDefinition(
        column="matches_played",
        label="Partidos",
        description="Partidos disputados",
        fmt="{}",
        is_key_stat=False,
        is_comparison_stat=False,
    ),
    "expected_goals": StatDefinition(
        column="expected_goals",
        label="xG",
        description="Goles esperados segun calidad de tiros",
        fmt="{:.2f}",
        plain_text_rules=_XG_RULES,
        is_leaderboard_stat=True,
    ),
    "shots_total": StatDefinition(
        column="shots_total",
        label="Tiros",
        description="Total de tiros realizados",
        fmt="{}",
        is_leaderboard_stat=True,
    ),
    "shots_on_target": StatDefinition(
        column="shots_on_target",
        label="Tiros al Arco",
        description="Tiros que van entre los tres palos",
        fmt="{}",
    ),
    "shot_conversion_pct": StatDefinition(
        column="shot_conversion_pct",
        label="Efectividad (%)",
        description="Porcentaje de tiros que terminan en gol",
        fmt="{:.1f}%",
        plain_text_rules=_CONVERSION_RULES,
    ),
    "key_passes_p90": StatDefinition(
        column="key_passes_p90",
        label="Pases Clave /90",
        description="Pases que generan ocasion de gol por cada 90 minutos",
        fmt="{:.2f}",
        plain_text_rules=_KEY_PASS_RULES,
        is_leaderboard_stat=True,
    ),
    "pass_accuracy_pct": StatDefinition(
        column="pass_accuracy_pct",
        label="Precision de Pases (%)",
        description="Porcentaje de pases completados",
        fmt="{:.1f}%",
        plain_text_rules=_PASS_RULES,
    ),
    "tackles_p90": StatDefinition(
        column="tackles_p90",
        label="Entradas /90",
        description="Entradas exitosas por cada 90 minutos",
        fmt="{:.2f}",
        plain_text_rules=_TACKLE_RULES,
        is_leaderboard_stat=True,
    ),
    "interceptions_p90": StatDefinition(
        column="interceptions_p90",
        label="Intercepciones /90",
        description="Balones cortados por cada 90 minutos",
        fmt="{:.2f}",
        plain_text_rules=_TACKLE_RULES,
    ),
    "duels_ground_won_p90": StatDefinition(
        column="duels_ground_won_p90",
        label="Duelos Ganados /90",
        description="Duelos en el suelo ganados por 90 min",
        fmt="{:.2f}",
    ),
    "duels_aerial_pct": StatDefinition(
        column="duels_aerial_pct",
        label="Duelos Aereos (%)",
        description="Porcentaje de duelos aereos ganados",
        fmt="{:.1f}%",
        plain_text_rules=_AERIAL_RULES,
    ),
    "dribbles_successful_p90": StatDefinition(
        column="dribbles_successful_p90",
        label="Regates /90",
        description="Regates exitosos por cada 90 minutos",
        fmt="{:.2f}",
        plain_text_rules=_DRIBBLE_RULES,
    ),
    "big_chances": StatDefinition(
        column="big_chances",
        label="Ocasiones Claras",
        description="Tiros con alta probabilidad de gol",
        fmt="{}",
    ),
    "xa": StatDefinition(
        column="xa",
        label="xA",
        description="Asistencias esperadas",
        fmt="{:.2f}",
    ),
    "progressive_carries_p90": StatDefinition(
        column="progressive_carries_p90",
        label="Conducciones Progresivas /90",
        description="Conducciones hacia el area rival por 90 min",
        fmt="{:.2f}",
    ),
    "clearances_p90": StatDefinition(
        column="clearances_p90",
        label="Despejes /90",
        description="Despejes por cada 90 minutos",
        fmt="{:.2f}",
    ),
    "fouls_won_p90": StatDefinition(
        column="fouls_won_p90",
        label="Faltas Recibidas /90",
        description="Faltas a favor por cada 90 minutos",
        fmt="{:.2f}",
    ),
    "yellow_cards": StatDefinition(
        column="yellow_cards",
        label="Amarillas",
        description="Tarjetas amarillas recibidas",
        fmt="{}",
        higher_is_better=False,
        is_key_stat=False,
        is_comparison_stat=False,
    ),
    "red_cards": StatDefinition(
        column="red_cards",
        label="Rojas",
        description="Tarjetas rojas recibidas",
        fmt="{}",
        higher_is_better=False,
        is_key_stat=False,
        is_comparison_stat=False,
    ),
}


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

def get(column: str) -> StatDefinition:
    """Look up a stat definition by DB column name."""
    if column not in _REGISTRY:
        return StatDefinition(
            column=column,
            label=column.replace("_", " ").title(),
            description="",
            fmt="{}",
        )
    return _REGISTRY[column]


def all_columns() -> list[str]:
    """All registered column names."""
    return list(_REGISTRY.keys())


def key_stats() -> list[str]:
    """Columns marked as key stats for infographics."""
    return [s.column for s in _REGISTRY.values() if s.is_key_stat]


def comparison_stats() -> list[str]:
    """Columns marked for H2H comparison."""
    return [s.column for s in _REGISTRY.values() if s.is_comparison_stat]


def leaderboard_stats() -> list[str]:
    """Columns available for leaderboards with their definitions."""
    return [s for s in _REGISTRY.values() if s.is_leaderboard_stat]


def higher_is_better(column: str) -> bool:
    """Whether a higher value is better for this stat."""
    return get(column).higher_is_better


def format_value(column: str, value) -> str:
    """Format a value using the stat's format string."""
    if value is None:
        return "N/A"
    return get(column).fmt.format(value)


def plain_text(column: str, percentile: int | None) -> str | None:
    """Generate plain-text description from registry rules."""
    if percentile is None:
        return None

    stat = get(column)

    # Tier
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

    # Flavor text from rules
    if stat.plain_text_rules:
        for threshold, msg in stat.plain_text_rules:
            if percentile >= threshold:
                return msg

    return tier
