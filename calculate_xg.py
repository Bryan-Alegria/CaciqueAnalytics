"""Train an xG prediction model and fill ALL NULL xG values across all competitions.

Uses RandomForestRegressor trained on Libertadores + Sudamericana data where
SofaScore provides real xG values, then predicts xG for all NULL rows.
"""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.db.session import get_connection

conn = get_connection()

# 1. Fetch training data (continental comps where xG is available)
print("=== FETCHING TRAINING DATA ===")
train_query = """
    SELECT
        pss.expected_goals as xg,
        pss.shots_total,
        pss.shots_on_target,
        pss.goals,
        pss.big_chances_missed,
        pss.shot_conversion_pct,
        pss.minutes_played,
        pss.rating,
        pss.assists,
        pss.key_passes_p90,
        pss.tackles_p90,
        pss.pass_accuracy_pct
    FROM player_season_stats pss
    JOIN seasons s ON s.id = pss.season_id
    WHERE s.competition_id IN (3, 4)  -- Libertadores, Sudamericana
      AND pss.expected_goals IS NOT NULL
"""
train_df = pd.read_sql(train_query, conn)
print(f"Raw training samples: {len(train_df)}")

# Drop rows where xG is NaN
train_df = train_df.dropna(subset=["xg"])
print(f"After dropping NaN xG: {len(train_df)}")
print(f"xG range: {train_df['xg'].min():.2f} to {train_df['xg'].max():.2f}")
print(f"xG mean: {train_df['xg'].mean():.2f}")

# 2. Fetch ALL data to predict (any competition where xG is NULL)
print("\n=== FETCHING ALL PREDICTION DATA ===")
predict_query = """
    SELECT
        pss.id as stat_id,
        p.full_name as player,
        t.name as team,
        s.year,
        c.name as competition,
        pss.shots_total,
        pss.shots_on_target,
        pss.goals,
        pss.big_chances_missed,
        pss.shot_conversion_pct,
        pss.minutes_played,
        pss.rating,
        pss.assists,
        pss.key_passes_p90,
        pss.tackles_p90,
        pss.pass_accuracy_pct
    FROM player_season_stats pss
    JOIN seasons s ON s.id = pss.season_id
    JOIN competitions c ON c.id = s.competition_id
    JOIN players p ON p.id = pss.player_id
    JOIN teams t ON t.id = pss.team_id
    WHERE pss.expected_goals IS NULL
"""
predict_df = pd.read_sql(predict_query, conn)
print(f"Prediction samples: {len(predict_df)}")

# 3. Build model pipeline
feature_cols = [
    "shots_total", "shots_on_target", "goals", "big_chances_missed",
    "shot_conversion_pct", "minutes_played", "rating", "assists",
    "key_passes_p90", "tackles_p90", "pass_accuracy_pct"
]

X_train = train_df[feature_cols]
y_train = train_df["xg"]

pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10))
])

# 4. Cross-validate
print("\n=== MODEL VALIDATION ===")
scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="neg_mean_absolute_error")
mae = -scores.mean()
print(f"Cross-validation MAE: {mae:.3f} xG")

# 5. Train on full training set
pipeline.fit(X_train, y_train)

# Feature importance
importances = pipeline.named_steps["model"].feature_importances_
print("\nFeature importances:")
for col, imp in sorted(zip(feature_cols, importances), key=lambda x: -x[1]):
    print(f"  {col:<25} {imp:.3f}")

# 6. Predict for ALL NULL rows
print("\n=== PREDICTING xG FOR ALL NULL ROWS ===")
X_predict = predict_df[feature_cols]
predictions = pipeline.predict(X_predict)

# Clip negative predictions to 0
predictions = np.clip(predictions, 0, None)

predict_df["predicted_xg"] = predictions

# Show sample predictions by competition
for comp in predict_df["competition"].unique():
    comp_df = predict_df[predict_df["competition"] == comp]
    print(f"\n  {comp} ({len(comp_df)} players):")
    sample = comp_df.nlargest(3, "goals")[["player", "team", "year", "goals", "shots_total", "shots_on_target", "predicted_xg"]]
    for _, row in sample.iterrows():
        g = row['goals'] if row['goals'] is not None else 0
        s = row['shots_total'] if row['shots_total'] is not None else 0
        sot = row['shots_on_target'] if row['shots_on_target'] is not None else 0
        print(f"    {row['player']:<22} G:{g:>2} S:{s:>2} SoT:{sot:>2} -> xG:{row['predicted_xg']:.2f}")

# 7. Update database
print("\n=== UPDATING DATABASE ===")
cur = conn.cursor()
updated = 0
for _, row in predict_df.iterrows():
    cur.execute(
        "UPDATE player_season_stats SET expected_goals = %s WHERE id = %s",
        (float(row["predicted_xg"]), int(row["stat_id"]))
    )
    updated += 1

conn.commit()
print(f"Updated {updated} rows with predicted xG")

# Verify - no NULLs and no NaNs
cur.execute("SELECT COUNT(*) FROM player_season_stats WHERE expected_goals IS NULL")
null_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM player_season_stats WHERE expected_goals = 'NaN'")
nan_count = cur.fetchone()[0]
print(f"Remaining NULL xG values: {null_count}")
print(f"Remaining NaN xG values: {nan_count}")

# Summary
cur.execute("""
    SELECT s.year, c.name, COUNT(*) as total, 
           MIN(expected_goals) as min_xg, 
           MAX(expected_goals) as max_xg, 
           ROUND(AVG(expected_goals), 2) as avg_xg
    FROM player_season_stats pss
    JOIN seasons s ON s.id = pss.season_id
    JOIN competitions c ON c.id = s.competition_id
    GROUP BY s.year, c.name, s.id
    ORDER BY s.id
""")
print("\n=== FINAL xG DISTRIBUTION ===")
for row in cur.fetchall():
    print(f"  {row[0]} {row[1]:<30} n={row[2]:>3}  min={row[3]:>5.2f}  max={row[4]:>5.2f}  avg={row[5]:>5.2f}")

cur.close()
conn.close()
print("\nDone!")
