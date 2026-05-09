"""Infographic rendering engine using matplotlib."""

import json
import os
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

CONFIG_PATH = Path(__file__).with_name("style_config.json")


class StyleConfig:
    """Load and expose style configuration."""

    def __init__(self, path: Path = CONFIG_PATH):
        with open(path, encoding="utf-8") as f:
            self._cfg = json.load(f)

    @property
    def canvas(self) -> dict:
        return self._cfg["canvas"]

    @property
    def colors(self) -> dict:
        return self._cfg["colors"]

    @property
    def fonts(self) -> dict:
        return self._cfg["fonts"]

    def team_colors(self, team_name: str) -> dict:
        return self._cfg["team_colors"].get(team_name, {"primary": "#333333", "secondary": "#cccccc"})


class Renderer:
    """Matplotlib figure factory."""

    def __init__(self, style: StyleConfig | None = None):
        self.style = style or StyleConfig()
        self.canvas = self.style.canvas
        self._logo_img: Image.Image | None = None

    def _load_logo(self) -> Image.Image | None:
        if self._logo_img is not None:
            return self._logo_img
        logo_cfg = self.style._cfg.get("logo", {})
        logo_path = logo_cfg.get("path", "")
        if not logo_path:
            return None
        resolved = Path(logo_path)
        if not resolved.is_absolute():
            # Resolve relative to project root (renderer.py is in src/infographics/)
            resolved = Path(__file__).resolve().parents[2] / logo_path
        if resolved.exists():
            self._logo_img = Image.open(resolved)
            return self._logo_img
        return None

    def new_figure(self, facecolor: str | None = None) -> plt.Figure:
        fig = plt.figure(
            figsize=(self.canvas["width"] / self.canvas["dpi"], self.canvas["height"] / self.canvas["dpi"]),
            dpi=self.canvas["dpi"],
            facecolor=facecolor or self.style.colors["background"],
        )
        return fig

    def save(self, fig: plt.Figure, path: str | Path) -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=self.canvas["dpi"], facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        return str(path)
