# CaciqueAnalytics

Statistical analysis and visualization applied to Chilean football,
starting with Colo-Colo and the Primera Division.

---

## Overview

This project collects, processes, and analyzes player-level statistics
from Chilean football competitions. The goal is to build ranking systems
by position, identify player profiles through clustering, and produce
publication-ready visualizations for social media content.

---

## Logo

![CaciqueAnalytics](assets/logo.png)

---

## Tech Stack

| Area                | Libraries                                      |
|---------------------|------------------------------------------------|
| Data collection     | soccerdata, requests, beautifulsoup4, selenium |
| Data processing     | pandas, numpy                                  |
| Machine learning    | scikit-learn, scipy                            |
| Visualization       | mplsoccer, matplotlib, seaborn, highlight-text |
| Notebook support    | jupyter, jupyterlab, ipykernel                 |
| Environment         | python-dotenv                                  |

---

## Project Structure

    CaciqueAnalytics/
    ├── assets/                  # Logos, player photos and brand resources
    ├── data/
    │   ├── raw/                 # Data as received from source APIs
    │   ├── processed/           # Cleaned and transformed datasets
    │   └── external/            # Manually downloaded external files
    ├── notebooks/
    │   ├── archive/             # Initial source exploration
    │   ├── 01_data_collection.ipynb
    │   ├── 02_data_processing.ipynb
    │   ├── 03_visualization.ipynb
    │   └── 04_<player>_<season>.ipynb
    ├── outputs/                 # Export-ready charts and infographics
    ├── docs/                    # Project documentation and references
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

| Source       | Coverage                           | Access   |
|--------------|------------------------------------|----------|
| SofaScore    | Match ratings, player stats, live  | Scraping |
| API-Football | Historical fixtures, team data     | Freemium |
| FBref        | Advanced stats, historical data    | Scraping |

---

## soccerdata Configuration

This project uses `soccerdata` to scrape FBref data for the Chilean
Primera Division. Since this league is not included by default, a
custom configuration file is required.

Copy `docs/soccerdata_league_dict.json` to:

    Windows  : C:\Users\<your-username>\soccerdata\config\league_dict.json
    Mac/Linux: ~/soccerdata/config/league_dict.json

Restart your Python session before running any notebook.

---

## Author

Bryan Alegria — [GitHub](https://github.com/Bryan-Alegria)