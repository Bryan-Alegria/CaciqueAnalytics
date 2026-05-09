"""Seed 2025 Chile Primera Division data for year-over-year comparison."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.db.session import get_connection
from src.etl.extract import extract_players
from src.etl.transform import transform_players

conn = get_connection()
cur = conn.cursor()

# Insert 2025 season
print("=== INSERTING SEASON 2025 ===")
cur.execute(
    """INSERT INTO seasons (competition_id, year, label, is_current)
       VALUES (%s, %s, %s, %s)
       ON CONFLICT (competition_id, year) DO NOTHING RETURNING id""",
    (1, 2025, "2025", False),
)
result = cur.fetchone()
if result:
    season_id = result[0]
    print(f"  Inserted season 2025 with id={season_id}")
else:
    cur.execute("SELECT id FROM seasons WHERE competition_id = %s AND year = %s", (1, 2025))
    season_id = cur.fetchone()[0]
    print(f"  Season 2025 already exists with id={season_id}")
conn.commit()

# Scrape 2025 data
print("\n=== SCRAPING 2025 PRIMERA CHILE ===")
raw_df = extract_players("Chile Primera Division", "2025", accumulation="total")
print(f"Total scraped: {len(raw_df)} players from {raw_df['team'].nunique()} teams")

# Seed any new teams
print("\n=== SEEDING TEAMS ===")
teams = sorted(raw_df["team"].unique())
new_teams = 0
for team_name in teams:
    cur.execute(
        "INSERT INTO teams (name, country) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id",
        (team_name, "Chile"),
    )
    if cur.fetchone():
        new_teams += 1
        print(f"  New team: {team_name}")
conn.commit()
print(f"New teams inserted: {new_teams}")

# Seed players and links
print("\n=== SEEDING PLAYERS & LINKS ===")
players_df = raw_df[["player", "team"]].drop_duplicates(subset=["player"])
new_players = 0
for _, row in players_df.iterrows():
    player_name = row["player"]
    team_name = row["team"]
    
    cur.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
    team_id = cur.fetchone()[0]
    
    cur.execute(
        "INSERT INTO players (full_name) VALUES (%s) ON CONFLICT (full_name) DO NOTHING RETURNING id",
        (player_name,),
    )
    result = cur.fetchone()
    if result:
        player_id = result[0]
        new_players += 1
    else:
        cur.execute("SELECT id FROM players WHERE full_name = %s", (player_name,))
        player_id = cur.fetchone()[0]
    
    cur.execute(
        """INSERT INTO player_team_seasons (player_id, team_id, season_id, position_id)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (player_id, team_id, season_id) DO NOTHING""",
        (player_id, team_id, season_id, None),
    )
conn.commit()
print(f"New players inserted: {new_players}")

# Load stats
print("\n=== LOADING PLAYER SEASON STATS ===")
clean_df = transform_players(raw_df, season_id=season_id)

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

inserted = updated = skipped = 0
for _, row in clean_df.iterrows():
    player_name = row.get("player_name")
    team_name = row.get("team_name")
    if not player_name or not team_name:
        skipped += 1
        continue
    
    cur.execute("SELECT id FROM players WHERE full_name = %s", (player_name,))
    p_row = cur.fetchone()
    if not p_row:
        skipped += 1
        continue
    player_id = p_row[0]
    
    cur.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
    t_row = cur.fetchone()
    if not t_row:
        skipped += 1
        continue
    team_id = t_row[0]
    
    values = [row.get(col) for col in columns]
    values[0] = player_id
    values[1] = season_id
    values[2] = team_id
    values[3] = "sofascore"
    
    cur.execute(
        """SELECT id FROM player_season_stats
           WHERE player_id = %s AND season_id = %s AND team_id = %s AND source = %s""",
        (player_id, season_id, team_id, "sofascore"),
    )
    existing = cur.fetchone()
    if existing:
        set_clause = ", ".join([f"{col} = %s" for col in columns[4:]])
        cur.execute(f"UPDATE player_season_stats SET {set_clause} WHERE id = %s", values[4:] + [existing[0]])
        updated += 1
    else:
        placeholders = ", ".join(["%s"] * len(columns))
        cur.execute(f"INSERT INTO player_season_stats ({', '.join(columns)}) VALUES ({placeholders})", values)
        inserted += 1

conn.commit()
print(f"Done: {inserted} inserted, {updated} updated, {skipped} skipped")

# Summary
print("\n=== SUMMARY ===")
cur.execute("SELECT COUNT(*) FROM teams")
print(f"Teams: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM players")
print(f"Players: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM seasons")
print(f"Seasons: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM player_team_seasons")
print(f"Player-team-season links: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM player_season_stats")
print(f"Player season stats: {cur.fetchone()[0]}")

cur.close()
conn.close()
print("\nDone!")
