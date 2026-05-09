"""Context engine: percentiles, league averages, plain-language descriptions."""

from dataclasses import dataclass
from typing import Any

from src.data_layers import stat_registry
from src.data_layers.providers import DbLeagueStatsProvider, LeagueStatsProvider


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


class ContextEngine:
    """Calculates league context (percentiles, averages) to make stats understandable.

    Does not depend on BaseDataLayer directly. Accepts a LeagueStatsProvider
    so it can be tested with mock data or used with different backends.
    """

    def __init__(
        self,
        season_year: int,
        competition_id: int,
        min_minutes: int = 270,
        provider: LeagueStatsProvider | None = None,
    ):
        self.season_year = season_year
        self.competition_id = competition_id
        self.min_minutes = min_minutes
        self.provider = provider or DbLeagueStatsProvider()

    def _get_league_values(self, column: str) -> list[float]:
        """Fetch all non-null values for a stat across the league."""
        return self.provider.get_values(
            column, self.season_year, self.competition_id, self.min_minutes
        )

    def _percentile(self, value: float, values: list[float], higher_is_better: bool) -> int:
        """Calculate percentile rank (0-100)."""
        if not values:
            return 50
        n = len(values)
        if higher_is_better:
            rank = sum(1 for v in values if v <= value)
        else:
            rank = sum(1 for v in values if v >= value)
        return int((rank / n) * 100)

    def get_context(self, column: str, value: float | None) -> StatContext:
        """Get full context for a single statistic."""
        meta = stat_registry.get(column)

        if value is None:
            return StatContext(
                value=None,
                label=meta.label,
                abbreviation=meta.label,
                description=meta.description,
                percentile=None,
                league_average=None,
                vs_average=None,
                plain_text=None,
                is_good_high=meta.higher_is_better,
            )

        values = self._get_league_values(column)
        is_good_high = meta.higher_is_better
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

        plain = stat_registry.plain_text(column, percentile)

        return StatContext(
            value=value,
            label=meta.label,
            abbreviation=meta.label,
            description=meta.description,
            percentile=percentile,
            league_average=round(league_average, 2) if league_average else None,
            vs_average=vs_average,
            plain_text=plain,
            is_good_high=is_good_high,
        )

    def get_all_contexts(self, stats_dict: dict[str, Any]) -> dict[str, StatContext]:
        """Get context for a dictionary of stats."""
        return {col: self.get_context(col, val) for col, val in stats_dict.items()}

    def close(self) -> None:
        """Release provider resources if supported."""
        if hasattr(self.provider, "close"):
            self.provider.close()
