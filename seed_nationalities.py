"""Seed common nationalities for Chilean football."""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

from src.db.session import get_connection

NATIONALITIES = [
    ("Chile", "CL"),
    ("Argentina", "AR"),
    ("Uruguay", "UY"),
    ("Brazil", "BR"),
    ("Peru", "PE"),
    ("Colombia", "CO"),
    ("Paraguay", "PY"),
    ("Bolivia", "BO"),
    ("Ecuador", "EC"),
    ("Venezuela", "VE"),
    ("Mexico", "MX"),
    ("Spain", "ES"),
    ("United States", "US"),
]

conn = get_connection()
cur = conn.cursor()

inserted = 0
for name, code in NATIONALITIES:
    cur.execute(
        "INSERT INTO nationalities (name, code) VALUES (%s, %s) ON CONFLICT (code) DO NOTHING RETURNING id",
        (name, code),
    )
    if cur.fetchone():
        inserted += 1
        print(f"  Inserted: {name} ({code})")
    else:
        print(f"  Already exists: {name} ({code})")

conn.commit()
cur.execute("SELECT COUNT(*) FROM nationalities")
print(f"\nTotal nationalities in DB: {cur.fetchone()[0]}")

cur.close()
conn.close()
print("Done!")
