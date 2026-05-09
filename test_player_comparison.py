"""Generate a test player comparison infographic."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.infographics.templates.player_comparison import PlayerComparison

comp = PlayerComparison()
path = comp.generate({
    "player_a": "Daniel Castro",
    "player_b": "Justo Giani",
    "season": 2026,
})
print(f"Saved to: {path}")
