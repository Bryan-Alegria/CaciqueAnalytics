# CaciqueAnalytics — Context

## Current Task

Code Refactoring (pre-Phase 4) is COMPLETE. All 5 deepening candidates implemented. Ready to begin Phase 4: Automation Layer.

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
- **Automation**: Windows Task Scheduler (Phase 4)
- **Testing**: pytest 9.0.3 (35 tests)
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

**Coverage:**
- 2025 Primera Chile: 463 stats
- 2026 Primera Chile: 392 stats
- 2026 Copa Libertadores: 39 stats (2 Chilean teams)
- 2026 Copa Sudamericana: 61 stats (3 Chilean teams)
- 2026 Copa de la Liga: 348 stats

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

Run: `python -m pytest tests/`

## Refactoring Status (COMPLETE)

| Candidate | Status | Files |
|-----------|--------|-------|
| 1. Stat Registry | COMPLETE | `src/data_layers/stat_registry.py` |
| 2. Plain Text Lookup | COMPLETE | `src/data_layers/context_engine.py` |
| 3. Query Seam | COMPLETE | `src/data_layers/queries.py` |
| 4. Colors Cache | COMPLETE | `src/data_layers/colors.py` |
| 5. Decouple ContextEngine | COMPLETE | `src/data_layers/providers.py`, `context_engine.py` |

## Handover Summary

### Current Task
- Building Phase 4: Automation Layer (GamedayDetector, Scheduler, Trigger, Notifier)
- PLAN.md Phase 4 section is the active roadmap
- No files currently in progress (ready to start `src/automation/`)

### Last Actions
1. Implemented all 5 architecture refactoring candidates (stat registry, query seam, provider injection, plain text lookup, colors cache)
2. Added 14 regression tests in `tests/test_data_layers/test_regression.py`
3. Cleaned repo: removed 10 unused files, cleared `__pycache__` and `.pytest_cache`
4. Rewrote README.md with professional usage documentation
5. Committed and pushed: `f56ebd5` (refactoring) + `e43f26d` (transparent logo fix)

### Verified
- Full test suite: **35/35 passing** with PostgreSQL running
- All data layers produce correct JSON structure
- ContextEngine works with injected provider
- Team colors cached correctly

### Next Actions
1. **Extend ETL to populate `matches` table** — `src/etl/matches.py`
2. **Build `GamedayDetector`** — `src/automation/detector.py`
3. **Build `AutomationTrigger`** — `src/automation/trigger.py`
4. **Build `Scheduler`** — `src/automation/scheduler.py`, `scheduler.ps1`
5. **Build `Notifier`** — `src/automation/notifier.py`
6. **Add `scrape_log` table migration** — `migrations/002_scrape_log.sql`
7. **Write automation tests** — `tests/test_automation/`

### Blockers
- `matches` table is EMPTY — must populate before GamedayDetector works

### Critical State
- **DB**: PostgreSQL 18 (start with `pg_ctl start -D "C:\Program Files\PostgreSQL\18\data"`)
- **DB name**: cacique_analytics
- **Python**: 3.12
- **Model**: Kimi v2.6 (implementation phase)
- **Branch**: main, up to date with origin
- **Latest commit**: `e43f26d` (transparent logo fix)
- **.env**: NOT committed, contains DB credentials
- **Dependencies**: psycopg2-binary, pytest, scikit-learn, jinja2, playwright, jupyter installed
- **Uncommitted changes**: None (all pushed)
- **Matches table**: EMPTY

## Files

- `PLAN.md` — Full implementation plan (5 phases)
- `AGENTS.md` — Agent instructions and conventions
- `CONTEXT.md` — This file
- `export_data.py` — CLI for data layer export
- `migrations/001_schema_optimization.sql` — Phase 1 DDL (applied)
- `src/config.py` — Config loader from .env
- `src/db/session.py` — PostgreSQL connection
- `src/scraper/` — SofaScore scraper and position classifier
- `src/etl/` — Extract, transform, load, orchestrator
- `src/infographics/` — HTML renderer + templates + style_config.json
- `src/data_layers/` — Modular data export system (9 files)
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
