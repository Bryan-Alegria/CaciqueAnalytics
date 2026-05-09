"""Team color loader from style config."""

import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "infographics" / "style_config.json"


def get_team_colors(team_name: str) -> dict[str, str]:
    """Get primary/secondary colors for a team name."""
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    colors = config.get("team_colors", {})

    # Exact match
    if team_name in colors:
        return colors[team_name]

    # Case-insensitive match
    for name, cols in colors.items():
        if name.lower() == team_name.lower():
            return cols

    # Fallback
    return {"primary": "#e94560", "secondary": "#ffffff"}
