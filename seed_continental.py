"""Seed Copa Libertadores and Copa Sudamericana 2026 data (Chilean teams only)."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import pandas as pd
from src.db.session import get_connection
from src.etl.extract import extract_players
from src.etl.transform import transform_players
from src.scraper.sofascore_client import SofaScoreClient

# Chilean teams we know are in continental comps 2026
KNOWN_CHILEAN_TEAMS = {
    "Coquimbo Unido", "Universidad Catolica",
    "Audax Italiano", "O'Higgins", "Palestino",
    # Also check for encoding variants
    "Universidad Catolica", "Universidad Católica",
    "O'Higgins", "O'Higgins",
    "Audax Italiano", "Audax Italiano",
    "Palestino", "Palestino",
    "Coquimbo Unido", "Coquimbo Unido",
}

def get_or_create_season(cur, competition_id, year):
    cur.execute(
        "INSERT INTO seasons (competition_id, year, label, is_current) VALUES (%s, %s, %s, %s) ON CONFLICT (competition_id, year) DO NOTHING RETURNING id",
        (competition_id, year, str(year), False),
    )
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("SELECT id FROM seasons WHERE competition_id = %s AND year = %s", (competition_id, year))
    return cur.fetchone()[0]

def get_team_id(cur, team_name):
    cur.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
    row = cur.fetchone()
    return row[0] if row else None

def get_or_create_player(cur, player_name):
    cur.execute("INSERT INTO players (full_name) VALUES (%s) ON CONFLICT (full_name) DO NOTHING RETURNING id", (player_name,))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("SELECT id FROM players WHERE full_name = %s", (player_name,))
    return cur.fetchone()[0]

def load_competition_stats(conn, cur, competition_name, competition_id, year, chilean_teams):
    season_id = get_or_create_season(cur, competition_id, year)
    print(f"\n=== {competition_name} {year} (season_id={season_id}) ===")
    
    # Scrape
    print("Scraping...")
    raw_df = extract_players(competition_name, str(year), accumulation="total")
    print(f"Total scraped: {len(raw_df)} players from {raw_df['team'].nunique()} teams")
    
    # Filter to Chilean teams
    filtered = raw_df[raw_df["team"].isin(chilean_teams)]
    print(f"Chilean teams filtered: {len(filtered)} players from {filtered['team'].nunique()} teams")
    
    if filtered.empty:
        print("No Chilean team data found. Skipping.")
        return 0, 0, 0
    
    print("Teams found:", sorted(filtered["team"].unique()))
    
    # Transform
    clean_df = transform_players(filtered, season_id=season_id)
    
    inserted = updated = skipped = 0
    for _, row in clean_df.iterrows():
        player_name = row.get("player_name")
        team_name = row.get("team_name")
        if not player_name or not team_name:
            skipped += 1
            continue
        
        team_id = get_team_id(cur, team_name)
        if not team_id:
            print(f"  SKIP: Team not in DB: {team_name}")
            skipped += 1
            continue
        
        player_id = get_or_create_player(cur, player_name)
        
        # Link player to team for season
        cur.execute(
            """INSERT INTO player_team_seasons (player_id, team_id, season_id, position_id)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (player_id, team_id, season_id) DO NOTHING""",
            (player_id, team_id, season_id, None),
        )
        
        # Build insert/update for player_season_stats
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
    return inserted, updated, skipped


conn = get_connection()
cur = conn.cursor()

# Fetch all Chilean team names from DB for matching
cur.execute("SELECT name FROM teams WHERE country = 'Chile'")
chilean_teams = {row[0] for row in cur.fetchall()}
print(f"Chilean teams in DB: {len(chilean_teams)}")

# 1. Libertadores
lib_inserted, lib_updated, lib_skipped = load_competition_stats(
    conn, cur, "Copa Libertadores", 3, 2026, chilean_teams
)

# 2. Sudamericana
sud_inserted, sud_updated, sud_skipped = load_competition_stats(
    conn, cur, "Copa Sudamericana", 4, 2026, chilean_teams
)

# Summary
print("\n=== FINAL SUMMARY ===")
cur.execute("SELECT COUNT(*) FROM seasons")
print(f"Seasons: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM player_team_seasons")
print(f"Player-team-season links: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM player_season_stats")
print(f"Player season stats: {cur.fetchone()[0]}")

cur.close()
conn.close()
print("\nDone!")
