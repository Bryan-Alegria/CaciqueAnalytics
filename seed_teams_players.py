"""Seed teams and players from scraped SofaScore data."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import psycopg2
from src.db.session import get_connection
from src.scraper.sofascore_client import SofaScoreClient

client = SofaScoreClient()
conn = get_connection()
cur = conn.cursor()

print("=== FETCHING DATA FROM SOFASCORE ===")
df = client.scrape_all_positions("Chile Primera Division", "2026")

# Deduplicate players
players_df = df[["player", "team"]].drop_duplicates(subset=["player"])
print(f"Unique players: {len(players_df)}")
print(f"Unique teams: {df['team'].nunique()}")

# Insert season first
print("\n=== INSERTING SEASON 2026 ===")
cur.execute(
    """INSERT INTO seasons (competition_id, year, label, is_current)
       VALUES (%s, %s, %s, %s)
       ON CONFLICT (competition_id, year) DO NOTHING RETURNING id""",
    (1, 2026, "2026", True),
)
result = cur.fetchone()
if result:
    season_id = result[0]
    print(f"  Inserted season 2026 with id={season_id}")
else:
    cur.execute("SELECT id FROM seasons WHERE competition_id = %s AND year = %s", (1, 2026))
    season_id = cur.fetchone()[0]
    print(f"  Season 2026 already exists with id={season_id}")
conn.commit()

# Seed teams
print("\n=== SEEDING TEAMS ===")
teams = sorted(df["team"].unique())
for team_name in teams:
    cur.execute(
        "INSERT INTO teams (name, country) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id",
        (team_name, "Chile"),
    )
    result = cur.fetchone()
    if result:
        print(f"  Inserted: {team_name}")
    else:
        print(f"  Already exists: {team_name}")
conn.commit()

# Seed players
print("\n=== SEEDING PLAYERS ===")
inserted = 0
for _, row in players_df.iterrows():
    player_name = row["player"]
    team_name = row["team"]
    
    # Find team_id
    cur.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
    team_row = cur.fetchone()
    if not team_row:
        print(f"  SKIP: Team not found for {player_name}")
        continue
    team_id = team_row[0]
    
    # Insert player
    cur.execute(
        "INSERT INTO players (full_name) VALUES (%s) ON CONFLICT (full_name) DO NOTHING RETURNING id",
        (player_name,),
    )
    result = cur.fetchone()
    if result:
        player_id = result[0]
        inserted += 1
    else:
        cur.execute("SELECT id FROM players WHERE full_name = %s", (player_name,))
        player_id = cur.fetchone()[0]
    
    # Link player to team for season
    cur.execute(
        """INSERT INTO player_team_seasons (player_id, team_id, season_id, position_id)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (player_id, team_id, season_id) DO NOTHING""",
        (player_id, team_id, season_id, None),
    )

conn.commit()
print(f"\nInserted {inserted} new players")

# Summary
print("\n=== SUMMARY ===")
cur.execute("SELECT COUNT(*) FROM teams")
print(f"Teams in DB: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM players")
print(f"Players in DB: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM seasons")
print(f"Seasons in DB: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM player_team_seasons")
print(f"Player-team-season links: {cur.fetchone()[0]}")

cur.close()
conn.close()
print("\nDone!")
