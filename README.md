<div align="center">
  <img src="assets/logo.png" alt="CaciqueAnalytics" width="160"/>

  # CaciqueAnalytics
</div>

Statistical analysis and visualization applied to Chilean football,
starting with Colo-Colo and the Primera Division.

---

## Overview

This project collects, processes, and analyzes player-level statistics
from Chilean football competitions. The goal is to build ranking systems
by position, identify player profiles through clustering, and produce
publication-ready visualizations for social media content.

---

## Tech Stack

| Area                | Libraries                                                         |
|---------------------|-------------------------------------------------------------------|
| Data collection     | LanusStats, pydoll-python, nest-asyncio, beautifulsoup4           |
| Data processing     | pandas, numpy, scipy                                              |
| Machine learning    | scikit-learn                                                      |
| Visualization       | mplsoccer, matplotlib, pillow, Faker                              |
| Notebook support    | jupyter, jupyterlab, ipykernel, ipywidgets                        |
| Environment         | python-dotenv                                                     |

---

## Project Structure

    CaciqueAnalytics/
    ├── assets/                  # Logos and brand resources (photos excluded)
    ├── data/
    │   ├── raw/                 # Data as received from source APIs
    │   ├── processed/           # Cleaned and transformed datasets
    │   └── external/            # Manually downloaded external files
    ├── notebooks/
    │   ├── archive/             # Initial source exploration
    │   ├── 01_data_collection.ipynb
    │   ├── 02_data_processing.ipynb
    │   ├── 03_visualization.ipynb
    │   ├── 04_jeyson_rojas_2026.ipynb
    │   ├── 05_sosa_vs_zaldivia_2026.ipynb
    │   └── 06_victor_felipe_mendez_2026.ipynb
    ├── outputs/
    │   ├── jeyson_rojas/        # Exported charts — Jeyson Rojas post
    │   ├── sosa_vs_zaldivia/    # Exported charts — Sosa vs Villagra post
    │   └── victor_felipe_mendez/# Exported charts — Víctor Felipe Méndez post
    ├── docs/                    # Project documentation and references
    ├── _extract_colors.py       # Diagnostic: dominant color inspection for asset PNGs
    ├── detect_red.py            # Extracts inaccurate pass coords from SofaScore screenshots
    ├── .env.example             # Environment variable template
    ├── .gitignore
    └── requirements.txt

---

## Setup

    # 1. Clone the repository
    git clone https://github.com/Bryan-Alegria/CaciqueAnalytics.git
    cd CaciqueAnalytics

    # 2. Create and activate virtual environment
    python -m venv venv
    venv\Scripts\activate

    # 3. Install dependencies
    pip install -r requirements.txt

    # 4. Configure environment variables
    # Copy .env.example to .env and fill in your API keys

---

## Data Sources

| Source       | Coverage                           | Access              |
|--------------|------------------------------------|---------------------|
| SofaScore    | Match ratings, player stats, live  | LanusStats + pydoll |

---

## Notes

- Player photo files (`assets/*.jpg`) are excluded from version control.
- Processed CSVs (`data/processed/`) and raw data (`data/raw/`) are also excluded.
- Run notebooks in order: `01` → `02` → `03` → `04` / `05` / `06`.
- `detect_red.py` and `_extract_colors.py` are standalone scripts; run them independently when rebuilding the inaccurate-pass estimates from new screenshots.

---

## Author

Bryan Alegria — [GitHub](https://github.com/Bryan-Alegria)