<p align="center">
  <img src="Infographics/Logo%20con%20Tipograf%C3%ADa%20HD%20Arreglado.png" alt="CaciqueAnalytics Logo" width="350"/>
</p>

<h1 align="center">CaciqueAnalytics</h1>

<p align="center">
  <strong>Automated data pipeline for Chilean football analytics</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#project-structure">Project Structure</a> •
  <a href="#data-coverage">Data Coverage</a>
</p>

---

## Overview

CaciqueAnalytics scrapes match and player statistics from SofaScore, processes them through an ETL pipeline, loads them into PostgreSQL, and exports structured JSON data layers for professional infographic creation in Canvas, Figma, or Photoshop.

**Pipeline:**
```
SofaScore API -> ETL (Python) -> PostgreSQL -> Data Layers -> JSON -> Infographics
```

**Coverage:**
- **Competitions**: Primera Division Chile, Copa de la Liga, Copa Libertadores, Copa Sudamericana
- **Seasons**: 2026 (primary), 2025 (comparison)
- **Data**: 1,303 player-season records, 587 players, 18 teams, 5 competitions

---

## Features

### Modular Data Layers

Export structured JSON for any player, comparison, or leaderboard:

- **Layer Identity**: Name, team, position, team colors
- **Layer Basic Stats**: Matches, minutes, goals, assists, cards
- **Layer Key Stats**: Rating, xG, shots, passes with **percentiles** and **plain text**
- **Layer Derived Stats**: Goals/90, contributions/90, minutes/goal, shot accuracy
- **Layer Summary**: Headline, subheadline, top stat for quick layout

### Context Engine

Every statistic includes league context:

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

**Tiers:**
- Elite (>95%)
- Destacado (>85%)
- Por Encima del Promedio (>70%)
- Promedio (>40%)
- Por Debajo del Promedio

### HTML Infographic Renderer (Optional)

Auto-generate PNG infographics from Jinja2 templates using Playwright:

```python
from src.infographics.html_renderer import HTMLRenderer
renderer = HTMLRenderer()
renderer.generate_player_card("Fernando Zampedri", season_year=2026, competition_id=1)
```

Templates:
- `player_card.html` — B/R Football inspired design (dark theme, red accent)
- Extensible template system for custom layouts

---

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Windows (PowerShell 7+)

### Installation

```powershell
# 1. Clone the repository
git clone https://github.com/tuusuario/CaciqueAnalytics.git
Set-Location CaciqueAnalytics

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
Copy-Item .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Start PostgreSQL
Start-Service -Name "postgresql-x64-18" -Verb RunAs
# Or: & "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" start -D "C:\Program Files\PostgreSQL\18\data"

# 6. Run database migrations
psql -U postgres -d cacique_analytics -f migrations/001_schema_optimization.sql

# 7. Run ETL pipeline
python src/etl/orchestrator.py
```

---

## Usage

### Data Export CLI (Spanish Commands)

```powershell
# Single player export
python export_data.py jugador -n "Fernando Zampedri" -s 2026 -c 1

# Head-to-head comparison
python export_data.py comparar --j1 "Fernando Zampedri" --j2 "Daniel Castro" -s 2026 -c 1

# Leaderboards
python export_data.py tabla -s 2026 -c 1
```

**Arguments:**
- `-n, --nombre`: Player full name
- `-s, --season`: Season year (2025 or 2026)
- `-c, --competition`: Competition ID (1 = Primera, etc.)
- `--j1, --jugador1`: First player for comparison
- `--j2, --jugador2`: Second player for comparison

### Output

Exports are saved to `Infographics/data/` as JSON files:

```json
{
  "layer_identity": {
    "player_name": "Fernando Zampedri",
    "team": "Universidad Catolica",
    "position": "Delantero",
    "team_colors": { "primary": "#0033A0", "secondary": "#FFFFFF" }
  },
  "layer_basic_stats": { "matches": 14, "minutes": 1260, "goals": 11, "assists": 2 },
  "layer_key_stats": {
    "goals": { "value": 11, "label": "Goles", "percentile": 100, ... },
    "rating": { "value": 7.5, "label": "Calificacion", "percentile": 95, ... }
  },
  "layer_derived_stats": {
    "goals_per_90": { "value": 0.79, "label": "Goles /90", ... },
    "minutes_per_goal": { "value": 114.5, "label": "Min/Gol", ... }
  },
  "layer_summary": {
    "headline": "Fernando Zampedri - Universidad Catolica",
    "subheadline": "Delantero | Primera Division 2026",
    "top_stat": { "value": 11, "label": "Goles" }
  }
}
```

### Python API

```python
from src.data_layers import PlayerDataLayer, ComparisonDataLayer, LeaderboardDataLayer
import json

# Single player
layer = PlayerDataLayer("Fernando Zampedri", season_year=2026, competition_id=1)
data = layer.build_layers()
layer.close()

with open("player.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Comparison
comp = ComparisonDataLayer("Fernando Zampedri", "Daniel Castro", 2026, 1)
data = comp.build_layers()
comp.close()

# Leaderboard
lb = LeaderboardDataLayer(2026, 1)
data = lb.build_layers()
lb.close()
```

---

## Project Structure

```
CaciqueAnalytics/
├── AGENTS.md                        # Agent instructions and conventions
├── CONTEXT.md                       # Domain language and current state
├── PLAN.md                          # Full implementation plan (5 phases)
├── export_data.py                   # CLI for data layer export
├── calculate_xg.py                  # xG prediction script (one-off)
├── verify_db.py                     # Database verification script
├── migrations/
│   └── 001_schema_optimization.sql  # Database schema
├── src/
│   ├── config.py                    # Environment configuration
│   ├── db/
│   │   └── session.py               # PostgreSQL connection manager
│   ├── scraper/
│   │   ├── sofascore_client.py      # SofaScore API client
│   │   └── position_classifier.py   # Player position classification
│   ├── etl/
│   │   ├── extract.py               # Data extraction
│   │   ├── transform.py             # Data cleaning and normalization
│   │   ├── load.py                  # Database upsert logic
│   │   └── orchestrator.py          # Pipeline orchestration
│   ├── infographics/
│   │   ├── html_renderer.py         # Playwright + Jinja2 renderer
│   │   ├── renderer.py              # Matplotlib renderer
│   │   ├── style_config.json        # Team colors and design tokens
│   │   └── templates/               # HTML/CSS templates
│   │       ├── html/player_card.html
│   │       └── css/br-football.css
│   └── data_layers/                 # Modular data export system
│       ├── base.py                  # Database connectivity base class
│       ├── stat_registry.py         # Central stat metadata registry
│       ├── queries.py               # Reusable SQL query builders
│       ├── providers.py             # League stats provider interface
│       ├── context_engine.py        # Percentiles and plain text
│       ├── colors.py                # Team color lookup (cached)
│       ├── player_layer.py          # Single player data export
│       ├── comparison_layer.py      # H2H comparison export
│       └── leaderboard_layer.py     # Top lists export
├── tests/
│   ├── test_data_layers/            # Data layer regression tests (14)
│   ├── test_etl/                    # ETL transform tests (5)
│   ├── test_infographics/           # Infographics engine tests (7)
│   └── test_scraper/                # Scraper tests (6)
├── Infographics/                    # Generated output (gitignored)
│   └── data/                        # JSON exports (gitignored)
├── .env.example                     # Environment template
├── .gitignore
└── requirements.txt
```

---

## Data Coverage

| Competition | Season | Records |
|-------------|--------|---------|
| Primera Division Chile | 2025 | 463 |
| Primera Division Chile | 2026 | 392 |
| Copa Libertadores | 2026 | 39 |
| Copa Sudamericana | 2026 | 61 |
| Copa de la Liga | 2026 | 348 |
| **Total** | | **1,303** |

### Data Quality

- 0 NULL values in stat columns
- 0 duplicate records
- 0 encoding issues
- 0 orphan records
- 100% xG coverage (predicted via RandomForest, CV MAE: 0.128)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Database | PostgreSQL 18 |
| Scraping | LanusStats (SofaScore wrapper) |
| ML | scikit-learn (RandomForest xG predictor) |
| Rendering | Playwright + Jinja2 |
| Testing | pytest 9.0.3 |
| Automation | Windows Task Scheduler (Phase 4) |

---

## Roadmap

- [x] Phase 1: Database schema optimization
- [x] Phase 2: Core ETL pipeline
- [x] Phase 3: Infographic data layers
- [ ] Phase 4: Automation layer (match detection, scheduler, notifier)
- [ ] Phase 5: Web dashboard and historical backfill

---

## Contributing

This is a personal project for Chilean football analytics. For agent-specific conventions, see `AGENTS.md`.

---

## License

MIT
