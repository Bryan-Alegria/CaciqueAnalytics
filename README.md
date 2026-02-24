# CaciqueAnalytics

Statistical analysis and machine learning applied to Chilean
football, starting with Colo-Colo and the Primera División.

## Overview

This project collects, processes, and analyzes player-level
statistics from Chilean football competitions. The goal is to
build ranking systems by position, identify player profiles
through clustering, and produce publication-ready visualizations
for social media content.

## Tech Stack

- **Data collection**: API-Football, SofaScore (via soccerdata)
- **Data processing**: Pandas, NumPy
- **Machine learning**: Scikit-learn
- **Visualization**: Mplsoccer, Matplotlib, Seaborn
- **Environment**: Python 3.11+, Jupyter

## Project Structure

    CaciqueAnalytics/
    ├── data/
    │   ├── raw/                 # Data as received from source APIs
    │   ├── processed/           # Cleaned and transformed datasets
    │   └── external/            # Manually downloaded external files
    ├── notebooks/
    │   ├── archive/             # Initial source exploration (API-Football, FBref, Sofascore)
    │   └── 01_data_collection.ipynb
    ├── src/
    │   ├── data/                # Data ingestion and preprocessing scripts
    │   ├── visualization/       # Reusable chart generation functions
    │   └── models/              # Machine learning model scripts
    ├── models/                  # Serialized trained models
    ├── outputs/                 # Export-ready charts and infographics
    └── docs/                    # Project documentation and references


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
    # Create a .env file and add your API keys (see .env.example)

## Data Sources

| Source      | Coverage                          | Access   |
|-------------|-----------------------------------|----------|
| SofaScore   | Match ratings, player stats, live | Scraping |
| API-Football| Historical fixtures, team data    | Freemium |

## Setup — soccerdata Configuration

This project uses `soccerdata` to scrape FBref data for the Chilean
Primera Division. Since this league is not included by default, a
custom configuration file is required.

Copy the file `docs/soccerdata_league_dict.json` to:

    Windows : C:\Users\<your-username>\soccerdata\config\league_dict.json
    Mac/Linux: ~/soccerdata/config/league_dict.json

Then restart your Python session before running any notebook.

## Author

Bryan Alegría — [GitHub](https://github.com/Bryan-Alegria)
