"""
CaciqueAnalytics ETL Pipeline - Main Orchestrator
Extrae datos de temporada 2026 desde SofaScore y carga en PostgreSQL
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """
    Orquestador principal del ETL
    Fase 1C: Temporada 2026 desde SofaScore
    """
    print(f"[{datetime.now()}] Iniciando ETL Pipeline - Fase 1C")
    print(f"Target: Temporada 2026 - Primera División de Chile")
    print(f"Fuente: SofaScore (league_id=11653, season=88493)")

    # TODO: Implementar flujo ETL
    # 1. Extract: SofaScore API
    # 2. Transform: Validación y normalización
    # 3. Load: PostgreSQL (idempotente)

    print(f"[{datetime.now()}] ETL Pipeline completado")

if __name__ == "__main__":
    main()
