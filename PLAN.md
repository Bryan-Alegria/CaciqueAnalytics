# CaciqueAnalytics — Implementation Plan

## Overview

ETL pipeline scraping Chilean football data (SofaScore) for Primera Division,
Copa Libertadores, and Copa Sudamericana (2026 + 2025 for comparison), loading
to PostgreSQL, and generating infographics for X/Twitter.

---

## Phase 1: DB Schema Optimization

### 1.1 Fix `teams` table — missing `fotmob_id`

```sql
ALTER TABLE teams ADD COLUMN fotmob_id INTEGER;
ALTER TABLE teams ADD CONSTRAINT teams_fotmob_id_key UNIQUE (fotmob_id);
CREATE INDEX idx_teams_fotmob_id ON teams (fotmob_id) WHERE fotmob_id IS NOT NULL;
```

### 1.2 Fix `competitions` table — missing `transfermarkt_id`

```sql
ALTER TABLE competitions ADD COLUMN transfermarkt_id INTEGER;
ALTER TABLE competitions ADD CONSTRAINT competitions_transfermarkt_id_key UNIQUE (transfermarkt_id);
CREATE INDEX idx_competitions_transfermarkt_id ON competitions (transfermarkt_id) WHERE transfermarkt_id IS NOT NULL;
```

### 1.3 Extend `player_season_stats` — SofaScore fields not yet covered

```sql
ALTER TABLE player_season_stats ADD COLUMN tackles_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN rating NUMERIC(4,2);
ALTER TABLE player_season_stats ADD COLUMN expected_goals NUMERIC(6,2);
ALTER TABLE player_season_stats ADD COLUMN big_chances_missed SMALLINT;
ALTER TABLE player_season_stats ADD COLUMN fouls_won_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN fouls_committed_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN accurate_crosses_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN long_pass_accuracy_pct NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN offsides_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN hit_woodwork SMALLINT;
ALTER TABLE player_season_stats ADD COLUMN shots_blocked SMALLINT;
ALTER TABLE player_season_stats ADD COLUMN dispossessed_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN dribbled_past_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN shot_conversion_pct NUMERIC(5,2);
```

### 1.4 Extend `player_match_stats` — match-level fields

```sql
ALTER TABLE player_match_stats ADD COLUMN sub_on_min SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN sub_off_min SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN expected_goals NUMERIC(5,2);
ALTER TABLE player_match_stats ADD COLUMN expected_assists NUMERIC(5,2);
ALTER TABLE player_match_stats ADD COLUMN fouls_won SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN fouls_committed SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN offsides SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN was_fouled SMALLINT;
```

### 1.5 Extend `team_season_stats` — team-level aggregates

```sql
ALTER TABLE team_season_stats ADD COLUMN clean_sheets SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN failed_to_score SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN possession_avg NUMERIC(5,2);
ALTER TABLE team_season_stats ADD COLUMN yellow_cards SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN red_cards SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN corners SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN fouls_committed SMALLINT;
```

### 1.6 Extend `matches` — match context fields

```sql
ALTER TABLE matches ADD COLUMN home_ht_score SMALLINT;
ALTER TABLE matches ADD COLUMN away_ht_score SMALLINT;
ALTER TABLE matches ADD COLUMN referee CHARACTER VARYING(100);
ALTER TABLE matches ADD COLUMN venue CHARACTER VARYING(150);
ALTER TABLE matches ADD COLUMN attendance INTEGER;
ALTER TABLE matches ADD COLUMN source CHARACTER VARYING(20);
ALTER TABLE matches ADD CONSTRAINT chk_match_source CHECK (source::text = ANY (ARRAY['sofascore'::character varying, 'fbref'::character varying, 'fotmob'::character varying]::text[]));
```

### 1.7 Add `seasons.is_current` flag

```sql
ALTER TABLE seasons ADD COLUMN is_current BOOLEAN DEFAULT false;
```

### 1.8 New table: `match_team_stats`

Per-match team-level statistics (the raw data behind team season stats):

```sql
CREATE TABLE match_team_stats (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id),
    team_id INTEGER NOT NULL REFERENCES teams(id),
    possession_pct NUMERIC(5,2),
    shots_total SMALLINT,
    shots_on_target SMALLINT,
    corners SMALLINT,
    fouls SMALLINT,
    yellow_cards SMALLINT,
    red_cards SMALLINT,
    offsides SMALLINT,
    passes_total SMALLINT,
    passes_accurate SMALLINT,
    pass_accuracy_pct NUMERIC(5,2),
    xg NUMERIC(5,2),
    big_chances SMALLINT,
    hit_woodwork SMALLINT,
    CONSTRAINT match_team_stats_match_team_key UNIQUE (match_id, team_id)
);
CREATE INDEX idx_mts_match ON match_team_stats (match_id);
CREATE INDEX idx_mts_team ON match_team_stats (team_id);
```

### 1.9 New table: `standings`

League table snapshots per matchday for historical tracking:

```sql
CREATE TABLE standings (
    id SERIAL PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES seasons(id),
    matchday SMALLINT NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    position SMALLINT NOT NULL,
    points SMALLINT NOT NULL,
    played SMALLINT DEFAULT 0,
    wins SMALLINT DEFAULT 0,
    draws SMALLINT DEFAULT 0,
    losses SMALLINT DEFAULT 0,
    goals_for SMALLINT DEFAULT 0,
    goals_against SMALLINT DEFAULT 0,
    goal_difference SMALLINT DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT standings_season_matchday_team_key UNIQUE (season_id, matchday, team_id)
);
CREATE INDEX idx_standings_season_matchday ON standings (season_id, matchday);
CREATE INDEX idx_standings_team ON standings (team_id);
```

### 1.10 New table: `scrape_log`

Audit trail for every ETL run:

```sql
CREATE TABLE scrape_log (
    id SERIAL PRIMARY KEY,
    run_started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    run_finished_at TIMESTAMP WITH TIME ZONE,
    source CHARACTER VARYING(20) NOT NULL,
    competition_id INTEGER REFERENCES competitions(id),
    season_id INTEGER REFERENCES seasons(id),
    position_group CHARACTER VARYING(5),
    records_fetched INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_skipped INTEGER,
    error_message TEXT,
    status CHARACTER VARYING(20) DEFAULT 'running',
    CONSTRAINT chk_scrape_log_status CHECK (status::text = ANY (ARRAY['running'::character varying, 'success'::character varying, 'partial'::character varying, 'failed'::character varying]::text[]))
);
CREATE INDEX idx_scrape_log_run_started ON scrape_log (run_started_at);
CREATE INDEX idx_scrape_log_competition ON scrape_log (competition_id);
CREATE INDEX idx_scrape_log_status ON scrape_log (status);
```

### 1.11 New table: `infographics_log`

Track generated infographics and their data windows:

```sql
CREATE TABLE infographics_log (
    id SERIAL PRIMARY KEY,
    type CHARACTER VARYING(50) NOT NULL,
    title CHARACTER VARYING(200),
    season_id INTEGER REFERENCES seasons(id),
    matchday SMALLINT,
    player_ids INTEGER[],
    team_ids INTEGER[],
    file_path CHARACTER VARYING(500),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status CHARACTER VARYING(20) DEFAULT 'draft',
    CONSTRAINT chk_infographic_status CHECK (status::text = ANY (ARRAY['draft'::character varying, 'ready'::character varying, 'posted'::character varying]::text[]))
);
```

### 1.12 Add missing indexes

```sql
CREATE INDEX idx_matches_status ON matches (status) WHERE status = 'scheduled';
CREATE INDEX idx_matches_matchday ON matches (matchday);
CREATE INDEX idx_players_name_trgm ON players USING gin (full_name gin_trgm_ops);
```

---

## Phase 2: Core ETL Pipeline

### 2.1 Project Structure

```
C:\Users\PC\Projects\CaciqueAnalytics\
  .git/
  .env.example              # Template for credentials (NEVER commit .env)
  AGENTS.md
  opencode.json
  requirements.txt
  alembic/                  # Database migrations
  src/
    __init__.py
    config.py               # DB connection, API keys from .env
    db/
      __init__.py
      models.py             # SQLAlchemy models (or psycopg2 raw queries)
      session.py            # Connection management
    scraper/
      __init__.py
      sofascore_client.py   # Direct SofaScore API client (no browser)
      parser.py             # Map SofaScore columns -> DB columns
      position_classifier.py # Assign position_id from player data
    etl/
      __init__.py
      extract.py            # Pull data from scraper
      transform.py          # Clean, normalize, compute per90 stats
      load.py               # Upsert into PostgreSQL
      orchestrator.py       # Run full pipeline for a competition
    infographics/
      __init__.py
      templates/
        player_card.py      # Individual player stat card
        player_comparison.py # Head-to-head comparison
        match_preview.py    # Pre-match stats + prediction
        match_report.py     # Post-match xG, shot map, events
        league_table.py     # Standings visualization
        season_trend.py     # Form guide, progression charts
      renderer.py           # Matplotlib/seaborn rendering engine
    automation/
      __init__.py
      scheduler.py          # Gameday trigger logic
      notifier.py           # Alerts when data is ready
  tests/
    __init__.py
    test_scraper/
    test_etl/
    test_infographics/
  Infographics/             # Output directory for generated images
```

### 2.2 Scraping Strategy

**SofaScore API (no browser):**

LanusStats uses Selenium. We'll write a direct HTTP client against
SofaScore's underlying REST API, which is public and returns JSON.

```python
# Pseudocode for sofascore_client.py
class SofaScoreClient:
    BASE = "https://api.sofascore.com/api/v1"

    def get_season_stats(self, tournament_id, season_id, accumulation):
        # GET /api/v1/season/{season_id}/statistics/{accumulation}
        ...

    def get_standings(self, tournament_id, season_id):
        # GET /api/v1/unique-tournament/{tournament_id}/season/{season_id}/standings/total
        ...
```

This avoids the Chrome window overhead entirely. Falls back to LanusStats
for endpoints not yet reverse-engineered.

**Scraping order (per gameday cycle):**

1. Detect which matches were played (matchday filter)
2. Scrape match results + team stats -> `matches`, `match_team_stats`
3. Scrape player match stats -> `player_match_stats`
4. Scrape updated league table -> `standings`
5. Scrape accumulated season stats -> `player_season_stats`, `team_season_stats`

**Continental filter:**

Scrape Libertadores/Sudamericana fully, then filter to Chilean teams via
`SELECT id FROM teams WHERE country = 'Chile'`. Only insert/update records
for Chilean teams. Skip non-Chilean records silently.

### 2.3 Position Classification

`position_classifier.py` assigns `position_id` to each player:

1. SofaScore already groups by GK/DEF/MID/FWD -> maps to `position_group`
2. For specific code (CB vs RB vs LB), use player name and historical data:
   - Check Transfermarkt API for position
   - Use heuristics: known players, common mappings
   - Manual override list in a JSON/YAML config
3. Store result in `player_team_seasons.position_id`

### 2.4 ETL Idempotency

Every load step uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE`:

```sql
INSERT INTO player_season_stats (player_id, season_id, team_id, source, goals, ...)
VALUES ($1, $2, $3, $4, $5, ...)
ON CONFLICT (player_id, season_id, team_id, source)
DO UPDATE SET goals = EXCLUDED.goals, ...
```

This makes every ETL run safe to re-execute.

### 2.5 2025 Historical Data

Run the same pipeline for season year=2025 after 2026 is loaded.
Use `season.year` column in queries to compare year-over-year.

---

## Phase 3: Infographic Engine

### 3.1 Template Architecture

Templates are Python classes inheriting from `BaseTemplate`:

```python
class BaseTemplate:
    width = 1080
    height = 1080  # Square for X/Twitter feed

    def query(self, db_session, params) -> DataFrame:
        """Fetch data from DB"""
        raise NotImplementedError

    def plot(self, data) -> plt.Figure:
        """Render matplotlib figure"""
        raise NotImplementedError

    def generate(self, db_session, params) -> str:
        """Full pipeline: query -> plot -> save -> return filepath"""
        ...
```

### 3.2 Template Types

| Template | Query | Visual |
|----------|-------|--------|
| Player Card | `player_season_stats` + `players` + `teams` | Radar chart + stat bars + photo placeholder |
| Player Comparison | Two player cards side by side, difference highlights | Split card with delta indicators |
| Match Preview | `team_season_stats` + `matches` (upcoming) | H2H record, form guide, xG comparison |
| Match Report | `player_match_stats` + `match_team_stats` | xG timeline, shot map, top performers |
| League Table | `standings` (latest matchday) | Styled table with form strings |
| Season Trend | `standings` (all matchdays) | Line chart of positions over time |
| Top Scorers | `player_season_stats` ORDER BY goals DESC | Leaderboard card |
| Team of the Week | `player_match_stats` where `matchday = N` | Formation graphic with ratings |

### 3.3 Style System

Colors, fonts, logos managed via a `style_config.json`:

```json
{
  "colors": {
    "primary": "#1a1a2e",
    "accent": "#e94560",
    "background": "#16213e",
    "text_light": "#ffffff",
    "text_dark": "#0f3460"
  },
  "team_colors": {
    "Colo Colo": {"primary": "#000000", "secondary": "#FFFFFF"},
    "Universidad de Chile": {"primary": "#004B87", "secondary": "#E5002B"}
  }
}
```

### 3.4 Output

Images saved to `Infographics/` directory with naming pattern:
`{type}_{season}_{matchday}_{timestamp}.png`

---

## Phase 4: Automation Layer

### 4.1 Gameday Detection

Monitor `matches` table for status changes:

```python
def get_next_gameday(db):
    return db.query("""
        SELECT DISTINCT matchday FROM matches
        WHERE season_id = (SELECT id FROM seasons WHERE is_current = true)
        AND status = 'scheduled'
        ORDER BY matchday LIMIT 1
    """)
```

After each match in a matchday finishes, run ETL for that competition.

### 4.2 Trigger Logic

```python
def check_and_run():
    pending = get_unprocessed_matchdays()
    for md in pending:
        run_etl_for_matchday(md.season_id, md.matchday)
        generate_infographics_for_matchday(md.season_id, md.matchday)
        notify_user("Data ready for matchday %d" % md.matchday)
```

Run via Windows Task Scheduler every 2 hours on gamedays.

### 4.3 Posting Flow (Manual)

1. Script finishes ETL + generates infographics
2. Notify: "Matchday X data ready. Check Infographics/"
3. User reviews, picks images, posts manually to X
4. User marks infographic as `posted` in `infographics_log`

---

## Phase 5: Polish & Expansion (Future)

- Primera B (Segunda Division) scraping — needs SofaScore league ID check
- Web dashboard (React + react-doctor) for browsing data
- Historical seasons backfill (2021-2024)
- Automated X posting (if desired later)
- Player similarity engine (ML: nearest neighbors on stat vectors)

---

## Execution Order

| Step | What | Model |
|------|------|-------|
| 1 | Run DB migration SQL (Phase 1) | Kimi v2.6 |
| 2 | Write `sofascore_client.py` + test scrape | Kimi v2.6 |
| 3 | Write ETL orchestrator + first load to DB | Kimi v2.6 |
| 4 | Verify data in DB, validate completeness | DeepSeek V4 Pro |
| 5 | Write infographic templates (one by one) | Kimi v2.6 |
| 6 | Write automation scheduler | Kimi v2.6 |
| 7 | End-to-end test: scrape -> ETL -> infographic | DeepSeek V4 Pro |
