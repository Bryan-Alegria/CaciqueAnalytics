"""Quick test to verify SofaScore scraper works."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.scraper.sofascore_client import SofaScoreClient

client = SofaScoreClient()

print("=== Testing Chile Primera Division 2026 ===")
print()

# Test: scrape just goalkeepers (small dataset, fast)
df = client.scrape_players("Chile Primera Division", "2026", position_group="Goalkeepers")
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print()
print("First 3 rows:")
print(df.head(3).to_string())
