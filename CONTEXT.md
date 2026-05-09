# CaciqueAnalytics — Context

## Current Task

Phase 5: Player Similarity Engine is COMPLETE. All 5 phases done. 70/70 tests passing.

## Domain Language

- **CaciqueAnalytics**: Data pipeline for Chilean football analytics.
- **Primera Chile / Primera Division**: Chilean top-flight league.
- **Copa de la Liga**: New 2026 tournament (SofaScore ID 32734, season 90922).
- **SofaScore**: Primary data source. API-based scraping via LanusStats.
- **Data Layer**: Modular JSON export (player, comparison, leaderboard) for infographic creation.
- **Context Engine**: Calculates percentiles, league averages, and plain-text descriptions.
- **Gameday / matchday**: A round of fixtures. ~30 per season.
- **ETL**: Extract (scrape SofaScore) -> Transform (clean, compute per90, predict xG) -> Load (PostgreSQL upsert).

## Tech Stack

- **Language**: Python 3.12
- **Database**: PostgreSQL 18 (local, manual start via pg_ctl)
- **DB name**: cacique_analytics
- **Scraping**: LanusStats + direct SofaScore API
- **Data Export**: Modular layers with ContextEngine (percentiles + plain text)
- **HTML Renderer**: Playwright + Jinja2 (optional, for auto-generated infographics)
- **Automation**: Windows Task Scheduler (Phase 4 — COMPLETE)
- **Testing**: pytest 9.0.3 (70 tests)
- **ML**: scikit-learn 1.8.0 (RandomForest xG predictor)

## Database Summary

16 tables. 5 competitions. 19 positions. 13 nationalities. Schema migration applied.

## Data Status

| Table | Count |
|-------|------:|
| teams | 18 |
| players | 587 |
| nationalities | 13 |
| seasons | 5 |
| player_season_stats | **1,303** |
| matches | **240** |
| scrape_log | 0 (new table) |

**Coverage:**
- 2025 Primera Chile: 463 stats
- 2026 Primera Chile: 392 stats
- 2026 Copa Libertadores: 39 stats (2 Chilean teams)
- 2026 Copa Sudamericana: 61 stats (3 Chilean teams)
- 2026 Copa de la Liga: 348 stats

**Match Data (NEW):**
- 240 matches for Primera Division 2026 (30 matchdays x 8 matches)
- 88 finished, 152 scheduled
- Team sofascore_ids populated for 16 teams
- Season sofascore_season_ids populated (2026=88493, 2025=71131)

**Data Quality Verification (ALL PASSED):**
- 0 NULL values in all stat columns
- 0 duplicate records (verified via unique constraints)
- 0 encoding issues (fixed double-encoded UTF-8)
- 0 orphan records (all FKs resolve)
- 0 impossible values (negative goals/minutes, ratings > 10, percentages > 100)
- 1 multi-team player: Mario Sandoval (2026: Deportes Concepcion + Audax Italiano)

**xG Status:** 100% filled. Predicted via RandomForest (CV MAE: 0.128) for rows where SofaScore returns NULL.

## Data Layers (Phase 3 — COMPLETE)

### Export CLI (Spanish)
```bash
python export_data.py jugador -n "Fernando Zampedri" -s 2026 -c 1
python export_data.py comparar --j1 "Fernando Zampedri" --j2 "Daniel Castro" -s 2026 -c 1
python export_data.py tabla -s 2026 -c 1
```

### Layer Structure
- **layer_identity**: Name, team, position, team colors (from style_config.json)
- **layer_basic_stats**: Matches, minutes, goals, assists, cards
- **layer_key_stats**: Rating, xG, shots, passes with **percentiles** and **plain text**
- **layer_derived_stats**: Goals/90, contributions/90, minutes/goal, shot accuracy
- **layer_summary**: Headline, subheadline, top stat for quick infographic layout

### Context Engine
Every stat includes:
- **percentile**: 0-100 rank vs league
- **vs_average**: "+1221% vs promedio" or "-10% vs promedio"
- **plain_text**: "Elite - Goleador de alto nivel", "Destacado", "Promedio", etc.

Tiers: Elite (>95%), Destacado (>85%), Por Encima del Promedio (>70%), Promedio (>40%), Por Debajo del Promedio.

### HTML Renderer (Optional)
- Playwright + Jinja2 templates
- B/R Football inspired design (dark theme, red accent, Bebas Neue font)
- Template: `player_card.html` (1080x1350px)
- Can be extended or ignored if user prefers Canvas/manual design

## Test Suite

35 passing tests:
- ETL transform: 5 tests
- xG model: 3 tests
- Scraper: 7 tests
- Infographics engine: 7 tests
- Data layers regression: 14 tests
- Automation: 26 tests
  - Detector: 8 tests (using real DB data)
  - Notifier: 6 tests
  - Trigger: 5 tests
  - MatchExtractor: 7 tests
- ML: 9 tests
  - SimilarityEngine: 9 tests

Run: `python -m pytest tests/`

## Refactoring Status (COMPLETE)

| Candidate | Status | Files |
|-----------|--------|-------|
| 1. Stat Registry | COMPLETE | `src/data_layers/stat_registry.py` |
| 2. Plain Text Lookup | COMPLETE | `src/data_layers/context_engine.py` |
| 3. Query Seam | COMPLETE | `src/data_layers/queries.py` |
| 4. Colors Cache | COMPLETE | `src/data_layers/colors.py` |
| 5. Decouple ContextEngine | COMPLETE | `src/data_layers/providers.py`, `context_engine.py` |

## Automation Layer (Phase 4 — COMPLETE)

### Components

| Component | File | Purpose |
|-----------|------|---------|
| MatchExtractor | `src/etl/matches.py` | Fetch fixtures from SofaScore, upsert to matches table |
| GamedayDetector | `src/automation/detector.py` | Detect matchdays, status changes, completion |
| AutomationTrigger | `src/automation/trigger.py` | Orchestrate detection, ETL, export |
| Notifier | `src/automation/notifier.py` | Console/Discord/Windows notifications |
| Scheduler | `src/automation/scheduler.py` | CLI entry point for automation cycles |
| Task Scheduler | `scheduler.ps1` | PowerShell wrapper for Windows Task Scheduler |

### MatchExtractor
- Reuses single browser session for all API calls (performance optimization)
- Fetches rounds -> matches per round -> parses -> upserts
- Maps SofaScore team IDs to internal DB team IDs via `teams.sofascore_id`
- Idempotent: safe to re-run

### GamedayDetector
- `get_today_matches()` — matches scheduled for today
- `get_matches_by_status()` — filter by status (finished, live, scheduled)
- `get_newly_finished()` — matches finished since given time
- `is_matchday_complete()` — all matches in matchday are finished
- `get_current_matchday()` — highest matchday with finished matches
- `get_upcoming_matchdays()` — future matchdays with scheduled matches

### AutomationTrigger
- `run()` — full cycle: update matches, detect finished, check completion, notify
- `dry_run()` — report what would happen without executing
- Processes all active seasons (is_current=true or has unfinished matches)

### Notifier
- Backends: console (default), discord (webhook), windows (toast)
- Methods: `matchday_complete()`, `etl_complete()`, `error()`
- Spanish messages for user-facing notifications

### Scheduler
- Python CLI: `python src/automation/scheduler.py [--competition ID] [--season ID] [--dry-run]`
- PowerShell wrapper: `scheduler.ps1` for Windows Task Scheduler
- Recommended: every 15 minutes on match days, every 2 hours otherwise

## ML / Player Similarity Engine (Phase 5 — COMPLETE)

### Component
| Component | File | Purpose |
|-----------|------|---------|
| SimilarityEngine | `src/ml/similarity.py` | ML-based player similarity using cosine similarity on normalized per-90 stat vectors |

### Features
- 19-dimensional stat vector (goals, assists, rating, xG, shots, passes, duels, etc.)
- StandardScaler normalization
- Cosine similarity from scikit-learn
- Filters: minimum 270 minutes, optional same-position-only
- CLI: `python export_data.py similares -n "Fernando Zampedri" -s 2026 -c 1 -t 5`

### Export Format
```json
{
  "jugador_objetivo": "Fernando Zampedri",
  "temporada": 2026,
  "competicion": 1,
  "total_jugadores_index": 251,
  "jugadores_similares": [
    {"nombre": "Sebastian Saez", "equipo": "Union La Calera", "similitud": 0.917}
  ]
}
```

## Handover Summary

### Current Task
- **ALL 5 PHASES COMPLETE**
- Phase 1: DB Schema
- Phase 2: Core ETL
- Phase 3: Data Layers / Export
- Phase 4: Automation
- Phase 5: ML Player Similarity
- 70/70 tests passing
- **Project is functionally complete per PLAN.md**

### Last Actions
1. Built `SimilarityEngine` (`src/ml/similarity.py`) with cosine similarity
2. Added `similares` CLI command to `export_data.py`
3. Wrote 9 ML tests (all passing)
4. Updated CONTEXT.md and PLAN.md with Phase 5 completion

### Verified
- Full test suite: **70/70 passing** with PostgreSQL running
- SimilarityEngine finds reasonable similar players (e.g., Zampedri ~ Saez: 0.917)
- CLI exports valid JSON with similar players
- All previous phases still working (regression tests pass)

### Next Actions
- **Project complete** per documented plan
- Optional expansions (not in PLAN.md): web dashboard, automated X posting, more competitions

### Blockers
- None

### Critical State
- **DB**: PostgreSQL 18 (start with `pg_ctl start -D "C:\Program Files\PostgreSQL\18\data"`)
- **DB name**: cacique_analytics
- **Python**: 3.12
- **Model**: Kimi v2.6 (implementation phase)
- **Branch**: main, up to date with origin
- **Latest commit**: `a7ccb7b` (transparent logo fix)
- **.env**: NOT committed, contains DB credentials
- **Dependencies**: psycopg2-binary, pytest, scikit-learn, jinja2, playwright, jupyter installed
- **Uncommitted changes**: Phase 4 implementation files (not yet committed)
- **Matches table**: 240 matches (88 finished, 152 scheduled)

## Files

- `PLAN.md` — Full implementation plan (5 phases)
- `AGENTS.md` — Agent instructions and conventions
- `CONTEXT.md` — This file
- `export_data.py` — CLI for data layer export
- `scheduler.ps1` — Windows Task Scheduler wrapper
- `migrations/001_schema_optimization.sql` — Phase 1 DDL (applied)
- `migrations/002_add_sofascore_season_id.sql` — Add sofascore_season_id (applied)
- `migrations/003_scrape_log.sql` — scrape_log table (applied)
- `src/config.py` — Config loader from .env
- `src/db/session.py` — PostgreSQL connection
- `src/scraper/` — SofaScore scraper and position classifier
- `src/etl/` — Extract, transform, load, orchestrator, matches
- `src/infographics/` — HTML renderer + templates + style_config.json
- `src/data_layers/` — Modular data export system (9 files)
- `src/automation/` — Automation layer (detector, trigger, notifier, scheduler)
  - `stat_registry.py` — Central stat metadata registry
  - `queries.py` — Reusable SQL query builders
  - `providers.py` — LeagueStatsProvider interface + DB implementation
  - `context_engine.py` — Percentiles + plain text
  - `player_layer.py` — Single player export
  - `comparison_layer.py` — H2H comparison
  - `leaderboard_layer.py` — Top lists
  - `colors.py` — Team color lookup (cached)
  - `base.py` — Database connectivity base
- `tests/` — pytest suite (35 tests)
- `calculate_xg.py` — xG prediction script (one-off)
- `verify_db.py` — Database verification script
- `Infographics/` — Output directory (gitignored)
- `Infographics/data/` — JSON exports (gitignored)
