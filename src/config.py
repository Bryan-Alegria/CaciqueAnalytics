"""Configuration loader. Reads from .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "cacique_analytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Application DB user
APP_DB_USER = os.getenv("APP_DB_USER", "cacique_app")
APP_DB_PASSWORD = os.getenv("APP_DB_PASSWORD", "")

# SofaScore competition IDs
SOFASCORE_LEAGUES = {
    "Primera Chile": 11653,
    "Copa Libertadores": 384,
    "Copa Sudamericana": 480,
}

# Season IDs (2026)
SEASONS_2026 = {
    11653: 88493,  # Primera Chile
    384: 87760,    # Libertadores
    480: 87770,    # Sudamericana
}

# 2025 for comparison
SEASONS_2025 = {
    11653: 71131,
    384: 70083,
    480: 70070,
}
