"""Analyze scraped data quality before commit."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import pandas as pd
from src.scraper.sofascore_client import SofaScoreClient

client = SofaScoreClient()

print("=== FETCHING ALL POSITIONS (2026 Primera Chile) ===")
print()

# Scrape all position groups
for pos in client.POSITION_GROUPS:
    df = client.scrape_players("Chile Primera Division", "2026", position_group=pos)
    print(f"{pos:>15}: {len(df):>3} players")
    if not df.empty:
        print(f"                  Teams: {df['team'].nunique():>2} unique")
        print(f"                  Avg rating: {df['rating'].mean():.2f}")
        print(f"                  Missing ratings: {df['rating'].isna().sum()}")
        print(f"                  Sample: {df['player'].iloc[0]}")
    print()

# Full dataset
print("=== FULL DATASET SUMMARY ===")
full = client.scrape_all_positions("Chile Primera Division", "2026")
print(f"Total players: {len(full)}")
print(f"Unique teams: {full['team'].nunique()}")
print(f"Columns: {len(full.columns)}")
print()

print("=== TEAMS REPRESENTED ===")
for team in sorted(full['team'].unique()):
    count = len(full[full['team'] == team])
    print(f"  {team:<30} {count:>3} players")

print()
print("=== DATA QUALITY CHECK ===")
print(f"Missing player names: {full['player'].isna().sum()}")
print(f"Missing team names: {full['team'].isna().sum()}")
print(f"Missing ratings: {full['rating'].isna().sum()}")
print(f"Missing minutes: {full['minutesPlayed'].isna().sum()}")
print(f"Missing goals: {full['goals'].isna().sum()}")
print(f"Zero-minute players: {(full['minutesPlayed'] == 0).sum()}")
