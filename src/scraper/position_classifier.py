"""Map scraped player data to position_id in the database."""

import logging
from typing import Optional

from src.db.session import get_cursor

logger = logging.getLogger(__name__)

# Mapping from SofaScore position group to position_group code
GROUP_MAP = {
    "Goalkeepers": "GK",
    "Defenders": "DEF",
    "Midfielders": "MID",
    "Forwards": "FWD",
}

# Common player -> position_id overrides (manual classification)
# Format: {player_name: position_code}
KNOWN_POSITIONS = {
    # Add known players here after observing their roles
    # e.g. "Fernando Zampedri": "CF",
}


def classify_position(
    player_name: str, position_group: str, team_name: str
) -> Optional[int]:
    """Return position_id for a player.

    Priority:
    1. Known positions lookup
    2. Default first position in the group
    """
    # Check known overrides
    if player_name in KNOWN_POSITIONS:
        code = KNOWN_POSITIONS[player_name]
        return _get_position_id_by_code(code)

    # Default to first position in group
    group = GROUP_MAP.get(position_group)
    if not group:
        return None

    return _get_first_position_id_in_group(group)


def _get_position_id_by_code(code: str) -> Optional[int]:
    with get_cursor() as cur:
        cur.execute("SELECT id FROM positions WHERE code = %s", (code,))
        row = cur.fetchone()
        return row["id"] if row else None


def _get_first_position_id_in_group(group: str) -> Optional[int]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT id FROM positions WHERE position_group = %s ORDER BY id LIMIT 1",
            (group,),
        )
        row = cur.fetchone()
        return row["id"] if row else None
