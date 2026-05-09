"""Populate player_season_stats from scraped SofaScore data."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import pandas as pd
from src.db.session import get_connection
from src.etl.extract import extract_players
from src.etl.transform import transform_players

print("=== EXTRACTING DATA ===")
raw_df = extract_players("Chile Primera Division", "2026", accumulation="total")
print(f"Extracted {len(raw_df)} rows")

print("\n=== TRANSFORMING ===")
# Season id = 1 (2026 Primera Chile)
clean_df = transform_players(raw_df, season_id=1)
print(f"Transformed {len(clean_df)} records")

print("\n=== LOADING TO DB ===")
conn = get_connection()
cur = conn.cursor()

inserted = updated = skipped = 0

for _, row in clean_df.iterrows():
    player_name = row.get("player_name")
    team_name = row.get("team_name")
    
    if not player_name or not team_name:
        skipped += 1
        continue
    
    # Resolve IDs
    cur.execute("SELECT id FROM players WHERE full_name = %s", (player_name,))
    p_row = cur.fetchone()
    if not p_row:
        print(f"  SKIP: Player not found: {player_name}")
        skipped += 1
        continue
    player_id = p_row[0]
    
    cur.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
    t_row = cur.fetchone()
    if not t_row:
        print(f"  SKIP: Team not found: {team_name}")
        skipped += 1
        continue
    team_id = t_row[0]
    
    # Build insert
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
    values[1] = 1  # season_id
    values[2] = team_id
    values[3] = "sofascore"
    
    # Check existing
    cur.execute(
        """SELECT id FROM player_season_stats
           WHERE player_id = %s AND season_id = %s AND team_id = %s AND source = %s""",
        (player_id, 1, team_id, "sofascore"),
    )
    existing = cur.fetchone()
    
    if existing:
        # Update
        set_clause = ", ".join([f"{col} = %s" for col in columns[4:]])
        cur.execute(
            f"UPDATE player_season_stats SET {set_clause} WHERE id = %s",
            values[4:] + [existing[0]],
        )
        updated += 1
    else:
        # Insert
        placeholders = ", ".join(["%s"] * len(columns))
        cur.execute(
            f"INSERT INTO player_season_stats ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )
        inserted += 1

conn.commit()
print(f"\nDone: {inserted} inserted, {updated} updated, {skipped} skipped")

cur.close()
conn.close()
