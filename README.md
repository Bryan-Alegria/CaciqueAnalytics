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
    │   ├── raw/            # Data as received from source APIs
    │   ├── processed/      # Cleaned and transformed datasets
    │   └── external/       # Manually downloaded external files
    ├── notebooks/          # Exploratory analysis and prototyping
    ├── src/
    │   ├── data/           # Data ingestion and preprocessing scripts
    │   ├── visualization/  # Reusable chart generation functions
    │   └── models/         # Machine learning model scripts
    ├── models/             # Serialized trained models
    ├── outputs/            # Export-ready charts and infographics
    └── docs/               # Project documentation and references

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

| Source       | Coverage                        | Access     |
|--------------|---------------------------------|------------|
| API-Football | Fixtures, squads, player stats  | Freemium   |
| SofaScore    | Match ratings, detailed metrics | Scraping   |
| FootyStats   | xG, corners, cards              | Freemium   |

## Author

Bryan Alegría — [GitHub](https://github.com/Bryan-Alegria)
