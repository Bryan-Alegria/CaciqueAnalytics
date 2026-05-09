"""Generate a test player card infographic."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.infographics.templates.player_card import PlayerCard

card = PlayerCard()
path = card.generate({"player_name": "Fernando Zampedri", "season": 2026})
print(f"Saved to: {path}")
