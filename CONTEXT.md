# CaciqueAnalytics — Context

## Current Task

Phase 3 (Infographic Data Layers) is COMPLETE. All data is now exportable as modular JSON layers for user-designed infographics. Phase 4 (Automation Layer) starts tomorrow, preceded by a code refactoring pass.

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
- **Database**: PostgreSQL 18 (local, manual start)
- **DB name**: cacique_analytics
- **Scraping**: LanusStats + direct SofaScore API
- **Data Export**: Modular layers with ContextEngine (percentiles + plain text)
- **HTML Renderer**: Playwright + Jinja2 (optional, for auto-generated infographics)
- **Automation**: Windows Task Scheduler (Phase 4)
- **Testing**: pytest 9.0.3 (21 tests)
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

21 passing tests:
- ETL transform: 5 tests
- xG model: 3 tests
- Scraper: 6 tests
- Infographics engine: 7 tests

Run: `python -m pytest tests/`

## Handover Summary

### Last Actions (Session 2026-05-09)
- Built modular `data_layers` package (7 files):
  - `base.py`: Database connectivity
  - `context_engine.py`: Percentiles, league averages, plain-text descriptions (Spanish)
  - `player_layer.py`: Single player data export
  - `comparison_layer.py`: H2H comparison with winner tracking
  - `leaderboard_layer.py`: Top scorers, assists, rating, xG, etc.
  - `colors.py`: Team color lookup from style_config.json
- Built `export_data.py` CLI with Spanish commands: `jugador`, `comparar`, `tabla`
- Built HTML renderer (`html_renderer.py`) with Playwright + Jinja2
- Created `player_card.html` template with B/R Football CSS design system
- Fixed all schema issues (position LEFT JOIN, team colors external lookup)
- Added Decimal-to-float JSON serialization
- Updated README with new features, data coverage, project structure
- Added project favicon
- Updated .gitignore for generated outputs
- All 21 tests passing
- Committed and pushed: `8042ec0` (14 files, 1,816 insertions)

### Next Actions (Tomorrow — 2026-05-10)
1. **Code Refactoring**
   - Audit codebase for duplicate code across modules
   - Unify database query patterns (single connection helper)
   - Consolidate stat column lists across layers
   - Extract shared formatting logic
   - Add type hints where missing
   - Review and simplify ContextEngine._plain_text() logic

2. **Phase 4: Automation Layer**
   - Extend ETL to populate `matches` table (currently empty)
   - Build `GamedayDetector`: monitor matches for status changes (scheduled -> live -> finished)
   - Build `Scheduler`: Windows Task Scheduler integration
   - Build `Trigger`: auto-run ETL when all matches in a matchday finish
   - Build `Notifier`: alert when data is ready (console/email/TBD)
   - Add `scrape_log` table for audit trail

3. **Tests**
   - Write pytest tests for data_layers package
   - Write tests for automation components
   - Verify full pipeline: scrape -> ETL -> data export

### Critical State
- **DB**: PostgreSQL 18 running, cacique_analytics, .env has credentials
- **Python**: 3.12
- **Model**: Currently Kimi v2.6 (implementation phase)
- **Branch**: main (14 commits ahead of origin/main -> now pushed)
- **.env**: Created with DB credentials, NOT committed
- **Dependencies**: psycopg2-binary, pytest, scikit-learn, jinja2, playwright installed
- **Uncommitted changes**: None (all pushed)
- **Matches table**: EMPTY — needs fixture extraction before automation works

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
- `src/data_layers/` — Modular data export system
- `tests/` — pytest suite (21 tests)
- `calculate_xg.py` — xG prediction script (one-off)
- `verify_db.py` — Database verification script
- `Infographics/` — Output directory (gitignored)
- `Infographics/data/` — JSON exports (gitignored)
