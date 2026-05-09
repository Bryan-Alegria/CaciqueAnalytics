"""Test updated templates with filters."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.infographics.templates.player_card import PlayerCard
from src.infographics.templates.top_scorers import TopScorers
from src.infographics.templates.player_comparison import PlayerComparison

print("=== TESTING PlayerCard ===")
card = PlayerCard()
path = card.generate({
    "player_name": "Fernando Zampedri",
    "season": 2026,
    "competition_id": 1,
})
print(f"PlayerCard saved: {path}")

print("\n=== TESTING TopScorers ===")
scorers = TopScorers()
path = scorers.generate({
    "season": 2026,
    "competition_id": 1,
    "limit": 10,
    "min_minutes": 270,
})
print(f"TopScorers saved: {path}")

print("\n=== TESTING PlayerComparison ===")
comp = PlayerComparison()
path = comp.generate({
    "player_a": "Daniel Castro",
    "player_b": "Justo Giani",
    "season": 2026,
    "competition_id": 1,
})
print(f"PlayerComparison saved: {path}")

print("\nAll templates generated successfully!")
