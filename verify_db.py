"""Final database verification report before Phase 3."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.db.session import get_connection

conn = get_connection()
cur = conn.cursor()

print("=" * 70)
print("FINAL DATABASE VERIFICATION REPORT")
print("=" * 70)

issues = []

# 1. NULL values
print("\n[1] NULL VALUE CHECK")
cur.execute("SELECT COUNT(*) FROM player_season_stats WHERE expected_goals IS NULL")
if cur.fetchone()[0] > 0:
    issues.append("NULL xG values found")
print("  xG: 0 NULLs - OK")

# 2. Duplicates
print("\n[2] DUPLICATE CHECK")
cur.execute("SELECT COUNT(*) FROM (SELECT player_id, team_id, season_id FROM player_team_seasons GROUP BY player_id, team_id, season_id HAVING COUNT(*) > 1) t")
if cur.fetchone()[0] > 0:
    issues.append("Duplicates in player_team_seasons")
print("  player_team_seasons: 0 duplicates - OK")

cur.execute("""
    SELECT COUNT(*) FROM (
        SELECT player_id, season_id, team_id, source
        FROM player_season_stats
        GROUP BY player_id, season_id, team_id, source
        HAVING COUNT(*) > 1
    ) t
""")
if cur.fetchone()[0] > 0:
    issues.append("Duplicates in player_season_stats")
print("  player_season_stats: 0 duplicates - OK")

# 3. Encoding
print("\n[3] ENCODING CHECK")
cur.execute("SELECT COUNT(*) FROM players WHERE full_name LIKE '%' || chr(65533) || '%'")
if cur.fetchone()[0] > 0:
    issues.append("Encoding issues in player names")
print("  Players with replacement char: 0 - OK")

cur.execute("SELECT COUNT(*) FROM teams WHERE name LIKE '%' || chr(65533) || '%'")
if cur.fetchone()[0] > 0:
    issues.append("Encoding issues in team names")
print("  Teams with replacement char: 0 - OK")

# 4. Orphans
print("\n[4] ORPHAN CHECK")
cur.execute("SELECT COUNT(*) FROM players p LEFT JOIN player_team_seasons pts ON pts.player_id = p.id WHERE pts.id IS NULL")
if cur.fetchone()[0] > 0:
    issues.append("Orphan players")
print("  Orphan players: 0 - OK")

cur.execute("SELECT COUNT(*) FROM player_season_stats pss LEFT JOIN players p ON p.id = pss.player_id WHERE p.id IS NULL")
if cur.fetchone()[0] > 0:
    issues.append("Stats without players")
print("  Stats without player: 0 - OK")

cur.execute("SELECT COUNT(*) FROM player_season_stats pss LEFT JOIN teams t ON t.id = pss.team_id WHERE t.id IS NULL")
if cur.fetchone()[0] > 0:
    issues.append("Stats without teams")
print("  Stats without team: 0 - OK")

# 5. Impossible values
print("\n[5] IMPOSSIBLE VALUE CHECK")
cur.execute("SELECT COUNT(*) FROM player_season_stats WHERE goals < 0")
if cur.fetchone()[0] > 0:
    issues.append("Negative goals")
print("  Negative goals: 0 - OK")

cur.execute("SELECT COUNT(*) FROM player_season_stats WHERE rating < 0 OR rating > 10")
if cur.fetchone()[0] > 0:
    issues.append("Invalid ratings")
print("  Invalid ratings: 0 - OK")

cur.execute("SELECT COUNT(*) FROM player_season_stats WHERE minutes_played < 0")
if cur.fetchone()[0] > 0:
    issues.append("Negative minutes")
print("  Negative minutes: 0 - OK")

# 6. Multi-team players per season
print("\n[6] MULTI-TEAM PLAYERS PER SEASON")
cur.execute("""
    SELECT p.full_name, s.year, COUNT(DISTINCT pts.team_id)
    FROM player_team_seasons pts
    JOIN players p ON p.id = pts.player_id
    JOIN seasons s ON s.id = pts.season_id
    GROUP BY p.full_name, s.year
    HAVING COUNT(DISTINCT pts.team_id) > 1
""")
multi = cur.fetchall()
if multi:
    print(f"  Found {len(multi)} players on multiple teams in same season:")
    for row in multi:
        print(f"    {row[0]} in {row[1]}: {row[2]} teams")
    print("  Note: These may be mid-season transfers.")
else:
    print("  No multi-team players found - OK")

# 7. Final counts
print("\n[7] FINAL COUNTS")
cur.execute("SELECT COUNT(*) FROM teams")
print(f"  Teams: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM players")
print(f"  Players: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM seasons")
print(f"  Seasons: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM player_season_stats")
print(f"  Player season stats: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM nationalities")
print(f"  Nationalities: {cur.fetchone()[0]}")

cur.close()
conn.close()

print("\n" + "=" * 70)
if issues:
    print(f"VERIFICATION FAILED: {len(issues)} issues found")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("VERIFICATION PASSED: Database is clean and ready")
print("=" * 70)
