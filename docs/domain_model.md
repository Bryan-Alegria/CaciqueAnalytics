# CaciqueAnalytics — Modelo de Dominio

**Estado:** Fase 1A completada / Fase 1B en progreso
**Última actualización:** 2026-03-15

---

## 1. Objetivo analítico

Recolectar, almacenar y analizar estadísticas de jugadores y equipos de la
Primera División de Chile (y competencias CONMEBOL asociadas) para producir:

- Rankings por posición granular
- Comparativas históricas temporada a temporada
- Perfiles individuales con percentiles de liga
- Visualizaciones para publicación en redes sociales

---

## 2. Fuentes de datos y cobertura temporal

| Fuente         | ID Chile   | Temporadas en LanusStats | Tipo de dato principal                          |
|----------------|------------|--------------------------|--------------------------------------------------|
| SofaScore      | `11653`    | 2023 – 2026 (4)          | Stats por partido, heatmaps, eventos, ratings    |
| FBref          | `35`       | 2021 – 2025 (5)          | Stats avanzadas por temporada (xG, xA, carries)  |
| FotMob         | `273`      | 2021 – 2025 (5)          | Shotmaps, percentiles de liga, stats de temporada|
| Transfermarkt  | `CLPD`     | Sin límite (dinámico)    | Valor de mercado, historial de transferencias    |

**Notas:**
- SofaScore es la fuente más granular a nivel de partido (coordenadas, eventos, ratings).
- FBref es la fuente más completa a nivel de temporada (xG, progressive carries, GCA, etc.).
- Transfermarkt es la única fuente de mercado; no tiene datos por partido.
- Las temporadas configuradas en LanusStats son el lower bound oficial. FBref tiene
  datos previos a 2021 pero requieren extender `functions.py` manualmente.

---

## 3. Taxonomía de posiciones

```
PORTERO
  └── GK      Portero

DEFENSA
  ├── CB      Central
  ├── RB      Lateral Derecho
  ├── LB      Lateral Izquierdo
  ├── RWB     Carrilero Derecho (lateral ofensivo)
  └── LWB     Carrilero Izquierdo (lateral ofensivo)

MEDIOCAMPO
  ├── CDM     Pivote Defensivo ("6")
  ├── CM_B2B  Mediocampista Box-to-Box ("8" — recupera y llega al área)
  ├── Mezzala Interior / "8" por banda (corta hacia dentro, tipo Bellingham)
  ├── Regista Distribuidor profundo ("8 bajo" — sale jugando, tipo Pirlo)
  ├── CAM     Mediocampista Ofensivo / Creativo ("10")
  ├── RM      Mediocampista Derecho
  └── LM      Mediocampista Izquierdo

ATAQUE
  ├── RW      Extremo Derecho
  ├── LW      Extremo Izquierdo
  ├── CF      Delantero Centro ("9")
  └── SS      Segundo Delantero
```

---

## 4. Métricas por grupo de posición

### GK — Portero
| Métrica                    | Fuente       | Por 90 |
|----------------------------|--------------|--------|
| paradas_totales            | SofaScore    | No     |
| porcentaje_paradas         | SofaScore    | No     |
| paradas_dificiles          | SofaScore    | No     |
| goles_concedidos           | SofaScore    | No     |
| goles_evitados_xg          | FBref        | No     |
| salidas_exitosas           | SofaScore    | Sí     |
| duelos_aereos_ganados      | SofaScore    | Sí     |

### CB / RB / LB / RWB / LWB — Defensores
| Métrica                    | Fuente       | Por 90 |
|----------------------------|--------------|--------|
| duelos_suelo_ganados       | SofaScore    | Sí     |
| duelos_aereos_pct          | SofaScore    | No     |
| intercepciones             | SofaScore    | Sí     |
| despejes                   | SofaScore    | Sí     |
| precision_pases_pct        | SofaScore    | No     |
| pelotas_largas_pct         | SofaScore    | No     |
| regates_exitosos           | SofaScore    | Sí     |
| centros_exitosos           | SofaScore    | Sí     |
| carries_progresivos        | FBref        | Sí     |

### CDM / CM_B2B / Mezzala / Regista — Mediocampistas
| Métrica                    | Fuente       | Por 90 | Aplica a             |
|----------------------------|--------------|--------|----------------------|
| duelos_suelo_ganados       | SofaScore    | Sí     | CDM, B2B             |
| intercepciones             | SofaScore    | Sí     | CDM, B2B             |
| recuperaciones             | SofaScore    | Sí     | CDM                  |
| precision_pases_pct        | SofaScore    | No     | Todos                |
| pases_clave                | SofaScore    | Sí     | B2B, Mezzala, CAM    |
| xA                         | FBref        | Sí     | CAM, Mezzala         |
| carries_progresivos        | FBref        | Sí     | Mezzala, Regista     |
| pases_ultimo_tercio        | FBref        | Sí     | Regista, CAM         |
| pelotas_largas_pct         | SofaScore    | No     | Regista              |
| regates_exitosos           | SofaScore    | Sí     | Mezzala, B2B         |

### CAM — Creativo / "10"
| Métrica                    | Fuente       | Por 90 |
|----------------------------|--------------|--------|
| pases_clave                | SofaScore    | Sí     |
| xA                         | FBref        | Sí     |
| regates_exitosos           | SofaScore    | Sí     |
| pases_ultimo_tercio        | FBref        | Sí     |
| asistencias                | SofaScore    | No     |

### RW / LW — Extremos
| Métrica                    | Fuente       | Por 90 |
|----------------------------|--------------|--------|
| regates_exitosos           | SofaScore    | Sí     |
| pases_clave                | SofaScore    | Sí     |
| centros_exitosos           | SofaScore    | Sí     |
| remates_totales            | SofaScore    | Sí     |
| xG                         | FBref        | Sí     |
| goles                      | SofaScore    | No     |

### CF / SS — Delanteros
| Métrica                    | Fuente       | Por 90 |
|----------------------------|--------------|--------|
| goles                      | SofaScore    | No     |
| xG                         | FBref        | Sí     |
| remates_totales            | SofaScore    | Sí     |
| remates_arco               | SofaScore    | Sí     |
| conversion_pct             | SofaScore    | No     |
| grandes_ocasiones          | SofaScore    | Sí     |
| duelos_aereos_pct          | SofaScore    | No     |
| pases_clave                | SofaScore    | Sí     |

---

## 5. Entidades del dominio (ERD conceptual)

```
nationalities  ─────────────────────────────────────────┐
  id (PK)                                                │
  name                                                   │
  code (ISO 3166-1 alpha-2)                              │
                                                         ▼
positions                                           players
  id (PK)                                             id (PK)
  code (GK, CB, RB...)                                full_name
  name_es                                             short_name
  group (GK/DEF/MID/FWD)                              nationality_id (FK)
                                                       position_id (FK)       ← posición natural
                                                       birth_date
                                                       height_cm
                                                       weight_kg
                                                       sofascore_id
                                                       fbref_id
                                                       transfermarkt_id
                                                       fotmob_id

teams
  id (PK)
  name
  short_name
  country
  sofascore_id
  fbref_id
  transfermarkt_id

competitions
  id (PK)
  name
  country
  type (league/cup/continental)
  sofascore_id
  fbref_id
  fotmob_id

seasons
  id (PK)
  competition_id (FK)
  year          ← ej. 2024
  label         ← ej. "2024" o "2024/25" según formato de la liga
  start_date
  end_date

matches
  id (PK)
  season_id (FK)
  home_team_id (FK)
  away_team_id (FK)
  match_date
  home_score
  away_score
  status (scheduled/finished/postponed)
  matchday
  sofascore_id
  fotmob_id

player_team_seasons              ← historial de qué equipo tuvo el jugador cada temporada
  id (PK)
  player_id (FK)
  team_id (FK)
  season_id (FK)
  position_id (FK)               ← posición usada esa temporada (puede diferir de la natural)

player_season_stats              ← agregado por temporada (FBref + FotMob + SofaScore)
  id (PK)
  player_id (FK)
  season_id (FK)
  team_id (FK)
  source (sofascore/fbref/fotmob)
  matches_played
  minutes_played
  goals
  assists
  yellow_cards
  red_cards
  -- métricas ofensivas
  shots_total
  shots_on_target
  xg
  xa
  key_passes_p90
  big_chances
  -- métricas defensivas
  duels_ground_won_p90
  duels_aerial_pct
  interceptions_p90
  clearances_p90
  -- métricas de creación/transición
  pass_accuracy_pct
  long_pass_accuracy_pct
  progressive_carries_p90
  passes_final_third_p90
  -- métricas de portero (NULL para no-GK)
  saves_total
  save_pct
  goals_prevented_xg
  -- percentiles dentro de la liga (calculados en procesamiento)
  percentile_league JSONB        ← {"xg_p90": 87, "duels_won_p90": 64, ...}

player_match_stats               ← granular por partido (SofaScore)
  id (PK)
  player_id (FK)
  match_id (FK)
  minutes_played
  rating
  goals
  assists
  yellow_cards
  red_cards
  -- métricas del partido
  shots_total
  shots_on_target
  key_passes
  duels_ground_won
  duels_aerial_won
  interceptions
  dribbles_successful
  pass_accuracy_pct
  -- datos posicionales
  heatmap_data JSONB             ← coordenadas x/y de posición dominante

player_market_values             ← Transfermarkt
  id (PK)
  player_id (FK)
  recorded_date
  value_eur
  team_id (FK)

team_season_stats                ← stats de equipo por temporada
  id (PK)
  team_id (FK)
  season_id (FK)
  source
  matches_played
  wins
  draws
  losses
  goals_for
  goals_against
  xg_for
  xg_against
  shots_total
  shots_on_target
  big_chances
  key_passes
  interceptions
  form_last_5 VARCHAR(5)         ← ej. "WWDLW"
```

---

## 6. Restricciones de diseño

- `player_season_stats` admite múltiples filas por jugador/temporada (una por fuente),
  diferenciadas por la columna `source`. Esto evita pérdida de datos al cruzar fuentes.
- `percentile_league` se almacena como JSONB para flexibilidad; las métricas
  varían según la posición del jugador.
- `heatmap_data` en `player_match_stats` se almacena como JSONB (array de puntos).
  La generación del heatmap se realiza en la capa de visualización.
- Los IDs externos (sofascore_id, fbref_id, etc.) son NULLable; no todos los
  jugadores están en todas las fuentes.

---

## 7. Comparación histórica — temporadas cubiertas

| Temporada | FBref | FotMob | SofaScore | Transfermarkt |
|-----------|-------|--------|-----------|---------------|
| 2021      | ✅    | ✅     | ❌        | ✅            |
| 2022      | ✅    | ✅     | ❌        | ✅            |
| 2023      | ✅    | ✅     | ✅        | ✅            |
| 2024      | ✅    | ✅     | ✅        | ✅            |
| 2025      | ✅    | ✅     | ✅        | ✅            |
| 2026      | ❌*   | ❌*    | ✅        | ✅            |

*FBref y FotMob son oficiales solo hasta 2025 en LanusStats 2.0.1. Se puede extender
manualmente en `functions.py` cuando los datos estén disponibles.

---

## 8. Tipos de contenido para redes sociales (mapeados a entidades)

| Formato de post         | Entidades involucradas                        |
|-------------------------|-----------------------------------------------|
| Perfil individual       | players + player_season_stats + positions     |
| Comparativa 1v1         | 2× players + player_season_stats              |
| Ranking de liga         | player_season_stats + percentile_league       |
| Heatmap + pases         | player_match_stats (heatmap_data)             |
| Preview de partido      | team_season_stats + matches + form_last_5     |
| Evolución temporal      | player_season_stats (multi-season, mismo player)|
| Underrated              | player_season_stats (percentil alto, equipo chico)|
| Perfil de portero       | player_season_stats (columnas GK)             |

---

## 9. Próximos pasos

1. Aprobación del usuario sobre este modelo.
2. Crear `src/migrations/001_initial_schema.sql` con las tablas definitivas.
3. Ejecutar migración contra `cacique_analytics` local.
4. Validar constraints y tipos de datos.
5. Documentar proceso ETL por fuente.
