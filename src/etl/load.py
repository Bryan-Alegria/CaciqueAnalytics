"""Load transformed data into PostgreSQL."""

import logging
from typing import Optional

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from src.db.session import get_connection

logger = logging.getLogger(__name__)


def load_players(
    df: pd.DataFrame, season_id: int, competition_id: int
) -> dict:
    """Upsert player season stats into player_season_stats table.

    Returns:
        Dict with counts: inserted, updated, skipped
    """
    if df.empty:
        return {"inserted": 0, "updated": 0, "skipped": 0}

    conn = get_connection()
    cur = conn.cursor()

    inserted = updated = skipped = 0

    try:
        for _, row in df.iterrows():
            # Resolve player_id and team_id from names
            player_id = _resolve_player(cur, row.get("player_name"))
            team_id = _resolve_team(cur, row.get("team_name"))

            if not player_id or not team_id:
                skipped += 1
                continue

            # Build upsert
            columns = [
                "player_id", "season_id", "team_id", "source",
                "goals", "assists", "yellow_cards", "red_cards",
                "minutes_played", "matches_played", "rating",
                "expected_goals", "big_chances_missed",
                "tackles_p90", "fouls_won_p90", "fouls_committed_p90",
                "accurate_crosses_p90", "long_pass_accuracy_pct",
                "offsides_p90", "hit_woodwork", "shots_blocked",
                "dispossessed_p90", "dribbled_past_p90",
                "shot_conversion_pct", "shots_total", "shots_on_target",
                "saves_total", "pass_accuracy_pct", "key_passes_p90",
                "interceptions_p90", "clearances_p90",
                "passes_final_third_p90", "dribbles_successful_p90",
                "duels_ground_won_p90", "duels_aerial_pct",
            ]

            values = [row.get(col) for col in columns]
            values[0] = player_id
            values[1] = season_id
            values[2] = team_id

            # Check if exists
            cur.execute(
                """SELECT id FROM player_season_stats
                   WHERE player_id = %s AND season_id = %s AND team_id = %s AND source = %s""",
                (player_id, season_id, team_id, row.get("source", "sofascore")),
            )
            existing = cur.fetchone()

            if existing:
                # Update
                set_clause = ", ".join([f"{col} = %s" for col in columns[4:]])
                cur.execute(
                    f"""UPDATE player_season_stats
                        SET {set_clause}
                        WHERE id = %s""",
                    values[4:] + [existing[0]],
                )
                updated += 1
            else:
                # Insert
                placeholders = ", ".join(["%s"] * len(columns))
                cur.execute(
                    f"""INSERT INTO player_season_stats ({', '.join(columns)})
                        VALUES ({placeholders})""",
                    values,
                )
                inserted += 1

        conn.commit()
        logger.info(f"Load complete: {inserted} inserted, {updated} updated, {skipped} skipped")

    except Exception as e:
        conn.rollback()
        logger.error(f"Load failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


def _resolve_player(cur, name: str) -> Optional[int]:
    """Find player_id by name, or None if not found."""
    if not name:
        return None
    cur.execute("SELECT id FROM players WHERE full_name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None


def _resolve_team(cur, name: str) -> Optional[int]:
    """Find team_id by name, or None if not found."""
    if not name:
        return None
    cur.execute("SELECT id FROM teams WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None
