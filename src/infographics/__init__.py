"""Infographics package."""

from src.infographics.renderer import Renderer, StyleConfig
from src.infographics.templates.player_card import PlayerCard
from src.infographics.templates.top_scorers import TopScorers
from src.infographics.templates.player_comparison import PlayerComparison

__all__ = ["Renderer", "StyleConfig", "PlayerCard", "TopScorers", "PlayerComparison"]
