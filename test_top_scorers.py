"""Generate a test top scorers infographic."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.infographics.templates.top_scorers import TopScorers

board = TopScorers()
path = board.generate({"season": 2026, "limit": 10})
print(f"Saved to: {path}")
