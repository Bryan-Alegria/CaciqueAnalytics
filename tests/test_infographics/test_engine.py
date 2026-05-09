"""Tests for infographics engine."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for testing
import matplotlib.pyplot as plt
import pytest

from src.infographics.renderer import Renderer, StyleConfig
from src.infographics.templates.base_template import BaseTemplate


class TestStyleConfig:
    """Unit tests for StyleConfig."""

    def test_loads_defaults(self):
        style = StyleConfig()
        assert style.canvas["width"] == 1080
        assert style.canvas["height"] == 1080
        assert "primary" in style.colors

    def test_team_colors_fallback(self):
        style = StyleConfig()
        colors = style.team_colors("Unknown Team")
        assert "primary" in colors
        assert "secondary" in colors

    def test_known_team_colors(self):
        style = StyleConfig()
        colors = style.team_colors("Colo-Colo")
        assert colors["primary"] == "#000000"


class TestRenderer:
    """Unit tests for Renderer."""

    def test_new_figure_dimensions(self):
        renderer = Renderer()
        fig = renderer.new_figure()
        assert isinstance(fig, plt.Figure)
        expected_w = 1080 / 150
        expected_h = 1080 / 150
        assert fig.get_figwidth() == expected_w
        assert fig.get_figheight() == expected_h
        plt.close(fig)

    def test_save_creates_file(self, tmp_path):
        renderer = Renderer()
        fig = renderer.new_figure()
        path = tmp_path / "test.png"
        result = renderer.save(fig, path)
        assert Path(result).exists()


class TestBaseTemplate:
    """Unit tests for BaseTemplate."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseTemplate()

    def test_requires_subclass_implementations(self):
        class Incomplete(BaseTemplate):
            pass
        with pytest.raises(TypeError):
            Incomplete()
