# CaciqueAnalytics

<p align="center">
  <img src="Infographics/Logo%20con%20Tipograf%C3%ADa%20HD%20Arreglado.png" alt="CaciqueAnalytics Logo" width="400"/>
</p>

Automated data pipeline for Chilean football analytics. Scrapes match and player
statistics, loads them into PostgreSQL, and generates structured data layers for
infographic creation.

## Data Pipeline

```
SofaScore API -> ETL (Python) -> PostgreSQL -> Data Layers -> JSON -> Infographics
```

- **Competitions**: Primera Division Chile, Copa de la Liga, Copa Libertadores, Copa Sudamericana
- **Seasons**: 2026 (primary), 2025 (comparison)
- **Data**: 1,303 player-season records, 587 players, 18 teams, 5 competitions

## Tech Stack

- **Python 3.12** — ETL pipeline, data processing, context engine
- **PostgreSQL 18** — Data storage (16 tables, normalized schema)
- **LanusStats** — SofaScore/FBRef/FotMob scraping wrapper
- **Playwright + Jinja2** — HTML-based infographic rendering
- **scikit-learn** — xG prediction model (RandomForest, CV MAE: 0.128)

## Quick Start

1. Start PostgreSQL: `Start-Service -Name "postgresql-x64-18" -Verb RunAs`
2. Copy `.env.example` to `.env` and fill in credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run ETL: `python src/etl/orchestrator.py`
5. Export data: `python export_data.py jugador -n "Fernando Zampedri" -s 2026 -c 1`

## Features

### Modular Data Layers

Export structured JSON data for infographic creation:

```bash
# Single player with context
python export_data.py jugador -n "Fernando Zampedri" -s 2026 -c 1

# Head-to-head comparison
python export_data.py comparar --j1 "Fernando Zampedri" --j2 "Daniel Castro" -s 2026 -c 1

# Leaderboards
python export_data.py tabla -s 2026 -c 1
```

Each export includes:
- **Identity layer**: Name, team, colors, position
- **Basic stats**: Matches, minutes, goals, assists
- **Key stats**: Rating, xG, shots, passes with **percentiles** and **plain text**
- **Derived stats**: Goals/90, contributions/90, minutes/goal
- **Context**: League averages, vs-average percentages, tier descriptions

### Context Engine

Every statistic includes context to make it understandable:

```json
{
  "goals": {
    "value": 11,
    "label": "Goles",
    "percentile": 100,
    "vs_average": "+1221% vs promedio",
    "plain_text": "Elite - Goleador de alto nivel"
  }
}
```

Tiers: Elite (>95%), Destacado (>85%), Por Encima del Promedio (>70%), Promedio (>40%), Por Debajo del Promedio.

### HTML Infographic Renderer (Optional)

Generate PNG infographics from Jinja2 templates using Playwright:

```python
from src.infographics.html_renderer import HTMLRenderer
renderer = HTMLRenderer()
renderer.generate_player_card("Fernando Zampedri", season_year=2026, competition_id=1)
```

Templates available:
- `player_card.html` — B/R Football inspired design
- `top_scorers.html` — Leaderboard layout
- `player_comparison.html` — Head-to-head

## Project Structure

```
.
├── AGENTS.md              # Agent instructions and conventions
├── CONTEXT.md             # Domain language and current state
├── PLAN.md                # Full implementation plan (5 phases)
├── export_data.py         # CLI for data layer export
├── migrations/            # Database migration files
├── src/
│   ├── scraper/           # SofaScore API client
│   ├── etl/               # Extract, transform, load pipeline
│   ├── infographics/      # HTML renderer + templates
│   ├── data_layers/       # Modular data export system
│   │   ├── base.py        # Database connectivity
│   │   ├── context_engine.py   # Percentiles and plain text
│   │   ├── player_layer.py     # Single player data
│   │   ├── comparison_layer.py # H2H comparison
│   │   └── leaderboard_layer.py # Top lists
│   └── config.py          # Competition mappings
├── Infographics/          # Generated output (gitignored)
└── tests/                 # Test suite (21 tests)
```

## Data Coverage

| Competition | Season | Records |
|-------------|--------|---------|
| Primera Division | 2025 | 463 |
| Primera Division | 2026 | 392 |
| Copa Libertadores | 2026 | 39 |
| Copa Sudamericana | 2026 | 61 |
| Copa de la Liga | 2026 | 348 |

## License

MIT
