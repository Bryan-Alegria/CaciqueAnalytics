# ETL Pipeline - CaciqueAnalytics

## Estructura

```
src/etl/
├── extractors/          # Extractores por fuente de datos
│   ├── base_extractor.py
│   ├── sofascore_extractor.py
│   ├── fbref_extractor.py
│   ├── fotmob_extractor.py
│   └── transfermarkt_extractor.py
├── transformers/        # Transformación y validación
│   ├── player_transformer.py
│   ├── match_transformer.py
│   └── stats_transformer.py
├── loaders/             # Carga a PostgreSQL
│   ├── postgres_loader.py
│   └── batch_loader.py
├── models/              # Modelos de datos
│   ├── player.py
│   ├── match.py
│   └── stats.py
├── utils/               # Utilidades compartidas
│   ├── logger.py
│   ├── validators.py
│   └── db_connection.py
└── main_etl.py          # Orquestador principal
```

## Prioridades Fase 1C

1. Temporada 2026 (actual)
2. Fuente: SofaScore (mejor cobertura 2026)
3. Datos: matches + player_match_stats + player_season_stats
4. Idempotencia: no duplicados en re-ejecuciones

## Dependencias requeridas

```
psycopg2-binary>=2.9.0
pandas>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

## Variables de entorno (.env)

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cacique_analytics
DB_USER=cacique_app
DB_PASSWORD=App@2026Cacique#Data!

SOFASCORE_LEAGUE_ID=11653
SOFASCORE_SEASON_2026=88493
```
