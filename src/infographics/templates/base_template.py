"""Base template for all infographic types."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd
from matplotlib import pyplot as plt

from src.infographics.renderer import Renderer, StyleConfig
from src.db.session import get_connection

# Resolve output dir relative to project root (3 levels above this file: src/infographics/templates/ -> root)
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "Infographics"


class BaseTemplate(ABC):
    """Abstract base for every infographic template."""

    template_type: str = "base"

    def __init__(self, style: StyleConfig | None = None):
        self.style = style or StyleConfig()
        self.renderer = Renderer(self.style)

    @abstractmethod
    def query(self, params: dict[str, Any]) -> pd.DataFrame:
        """Fetch data from the database."""
        ...

    @abstractmethod
    def plot(self, data: pd.DataFrame) -> plt.Figure:
        """Render a matplotlib figure."""
        ...

    def generate(self, params: dict[str, Any]) -> str:
        """Full pipeline: query -> plot -> save -> return filepath."""
        data = self.query(params)
        fig = self.plot(data)
        filename = self._filename(params)
        path = OUTPUT_DIR / filename
        return self.renderer.save(fig, path)

    def _filename(self, params: dict[str, Any]) -> str:
        season = params.get("season", "2026")
        matchday = params.get("matchday", "")
        suffix = params.get("suffix", self.template_type)
        if matchday:
            return f"{suffix}_{season}_md{matchday}.png"
        return f"{suffix}_{season}.png"
