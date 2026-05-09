# CaciqueAnalytics

Automated data pipeline for Chilean football analytics. Scrapes match and player
statistics, loads them into PostgreSQL, and generates infographics for social
media posting.

## Data Pipeline

```
SofaScore API -> ETL (Python) -> PostgreSQL -> matplotlib -> Infographics -> X/Twitter
```

- **Competitions**: Primera Division Chile, Copa Chile, Copa Libertadores, Copa Sudamericana
- **Seasons**: 2026 (primary), 2025 (comparison)
- **Cadence**: Automated after each gameday

## Tech Stack

- **Python 3.12** — ETL pipeline, data processing, visualization
- **PostgreSQL 18** — Data storage (16 tables, normalized schema)
- **LanusStats v2.1.6** — SofaScore/FBRef/FotMob scraping wrapper
- **matplotlib + seaborn** — Infographic generation

## Quick Start

1. Start PostgreSQL: `Start-Service -Name "postgresql-x64-18" -Verb RunAs`
2. Copy `.env.example` to `.env` and fill in credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run ETL: `python src/etl/orchestrator.py`

## Project Structure

```
.
├── AGENTS.md              # Agent instructions and conventions
├── CONTEXT.md             # Domain language and current state
├── PLAN.md                # Full implementation plan (5 phases)
├── migrations/            # Database migration files
├── src/
│   ├── scraper/           # SofaScore API client
│   ├── etl/               # Extract, transform, load pipeline
│   ├── infographics/      # Template-based image generation
│   └── automation/        # Scheduler and notifications
├── Infographics/          # Generated image output
└── tests/                 # Test suite
```

## License

MIT
