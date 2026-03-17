-- =============================================================================
-- Migración inicial: CaciqueAnalytics
-- Número: 001
-- Descripción: Schema base para estadísticas del fútbol chileno
-- Ejecutar como: psql -U cacique_app -d cacique_analytics -f 001_initial_schema.sql
-- =============================================================================

-- Extensión para timestamps con zona horaria consistentes
SET timezone = 'America/Santiago';


-- -----------------------------------------------------------------------------
-- 1. NATIONALITIES — Países y nacionalidades de los jugadores
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nationalities (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    code        CHAR(2)      NOT NULL UNIQUE  -- Código ISO 3166-1 alpha-2 (ej. CL, AR, BR)
);


-- -----------------------------------------------------------------------------
-- 2. POSITIONS — Taxonomía granular de posiciones
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS positions (
    id               SERIAL PRIMARY KEY,
    code             VARCHAR(10)  NOT NULL UNIQUE, -- GK, CB, STP, SW, RB, LB, ...
    name_es          VARCHAR(60)  NOT NULL,
    position_group   VARCHAR(5)   NOT NULL,
    CONSTRAINT chk_position_group CHECK (position_group IN ('GK', 'DEF', 'MID', 'FWD'))
);

-- Datos semilla: posiciones completas del proyecto
INSERT INTO positions (code, name_es, position_group) VALUES
    -- Portero
    ('GK',      'Portero',                       'GK'),
    -- Defensas
    ('CB',      'Central',                       'DEF'),
    ('STP',     'Stopper',                       'DEF'),
    ('SW',      'Líbero / Sweeper',              'DEF'),
    ('RB',      'Lateral Derecho',               'DEF'),
    ('LB',      'Lateral Izquierdo',             'DEF'),
    ('RWB',     'Carrilero Derecho',             'DEF'),
    ('LWB',     'Carrilero Izquierdo',           'DEF'),
    -- Mediocampistas
    ('CDM',     'Pivote Defensivo',              'MID'),
    ('CM_B2B',  'Mediocampista Box-to-Box',      'MID'),
    ('Mezzala', 'Interior / Mezzala',            'MID'),
    ('Regista', 'Distribuidor Profundo',         'MID'),
    ('CAM',     'Mediocampista Ofensivo',        'MID'),
    ('RM',      'Mediocampista Derecho',         'MID'),
    ('LM',      'Mediocampista Izquierdo',       'MID'),
    -- Ataque
    ('RW',      'Extremo Derecho',               'FWD'),
    ('LW',      'Extremo Izquierdo',             'FWD'),
    ('CF',      'Delantero Centro',              'FWD'),
    ('SS',      'Segundo Delantero',             'FWD')
ON CONFLICT (code) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 3. COMPETITIONS — Ligas y copas
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competitions (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(150) NOT NULL UNIQUE,
    country        VARCHAR(50),
    type           VARCHAR(20),
    sofascore_id   INTEGER UNIQUE,
    fbref_id       INTEGER UNIQUE,
    fotmob_id      INTEGER UNIQUE,
    CONSTRAINT chk_competition_type CHECK (type IN ('league', 'cup', 'continental'))
);

-- Datos semilla: competencias de interés inicial
INSERT INTO competitions (name, country, type, sofascore_id, fbref_id, fotmob_id) VALUES
    ('Primera División de Chile', 'Chile',  'league',      11653, 35, 273),
    ('Copa Chile',                'Chile',  'cup',         NULL,  NULL, NULL),
    ('Copa Libertadores',         NULL,     'continental', 384,   14,  42),
    ('Copa Sudamericana',         NULL,     'continental', 480,   NULL, NULL)
ON CONFLICT (name) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 4. TEAMS — Equipos
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS teams (
    id                SERIAL PRIMARY KEY,
    name              VARCHAR(150) NOT NULL,
    short_name        VARCHAR(50),
    country           VARCHAR(50),
    sofascore_id      INTEGER UNIQUE,
    fbref_id          VARCHAR(20) UNIQUE,
    transfermarkt_id  INTEGER UNIQUE,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 5. PLAYERS — Jugadores
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
    id                SERIAL PRIMARY KEY,
    full_name         VARCHAR(150) NOT NULL,
    short_name        VARCHAR(80),
    nationality_id    INTEGER REFERENCES nationalities(id),
    position_id       INTEGER REFERENCES positions(id),  -- Posición natural del jugador
    birth_date        DATE,
    height_cm         SMALLINT,
    weight_kg         SMALLINT,
    sofascore_id      INTEGER UNIQUE,
    fbref_id          VARCHAR(20) UNIQUE,
    transfermarkt_id  INTEGER UNIQUE,
    fotmob_id         INTEGER UNIQUE,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 6. SEASONS — Temporadas por competencia
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seasons (
    id               SERIAL PRIMARY KEY,
    competition_id   INTEGER NOT NULL REFERENCES competitions(id),
    year             SMALLINT NOT NULL,             -- Año de inicio (ej. 2024)
    label            VARCHAR(10) NOT NULL,          -- "2024" o "2024/25"
    start_date       DATE,
    end_date         DATE,
    UNIQUE (competition_id, year)
);


-- -----------------------------------------------------------------------------
-- 7. MATCHES — Partidos
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS matches (
    id             SERIAL PRIMARY KEY,
    season_id      INTEGER NOT NULL REFERENCES seasons(id),
    home_team_id   INTEGER NOT NULL REFERENCES teams(id),
    away_team_id   INTEGER NOT NULL REFERENCES teams(id),
    match_date     TIMESTAMPTZ,
    home_score     SMALLINT,
    away_score     SMALLINT,
    status         VARCHAR(15) DEFAULT 'scheduled',
    matchday       SMALLINT,
    sofascore_id   INTEGER UNIQUE,
    fotmob_id      INTEGER UNIQUE,
    CONSTRAINT chk_match_status CHECK (status IN ('scheduled', 'finished', 'postponed', 'cancelled')),
    CONSTRAINT chk_different_teams CHECK (home_team_id <> away_team_id)
);


-- -----------------------------------------------------------------------------
-- 8. PLAYER_TEAM_SEASONS — Historial de equipo por temporada
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_team_seasons (
    id           SERIAL PRIMARY KEY,
    player_id    INTEGER NOT NULL REFERENCES players(id),
    team_id      INTEGER NOT NULL REFERENCES teams(id),
    season_id    INTEGER NOT NULL REFERENCES seasons(id),
    position_id  INTEGER REFERENCES positions(id),  -- Posición usada esa temporada
    UNIQUE (player_id, team_id, season_id)
);


-- -----------------------------------------------------------------------------
-- 9. PLAYER_SEASON_STATS — Estadísticas de jugador por temporada
--    Admite múltiples filas por (player, season, team) diferenciadas por source
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_season_stats (
    id                        SERIAL PRIMARY KEY,
    player_id                 INTEGER NOT NULL REFERENCES players(id),
    season_id                 INTEGER NOT NULL REFERENCES seasons(id),
    team_id                   INTEGER NOT NULL REFERENCES teams(id),
    source                    VARCHAR(20) NOT NULL,
    -- Estadísticas base
    matches_played            SMALLINT,
    minutes_played            SMALLINT,
    goals                     SMALLINT,
    assists                   SMALLINT,
    yellow_cards              SMALLINT,
    red_cards                 SMALLINT,
    -- Ofensivas
    shots_total               SMALLINT,
    shots_on_target           SMALLINT,
    xg                        NUMERIC(6,2),
    xa                        NUMERIC(6,2),
    key_passes_p90            NUMERIC(5,2),
    big_chances               SMALLINT,
    -- Defensivas
    duels_ground_won_p90      NUMERIC(5,2),
    duels_aerial_pct          NUMERIC(5,2),
    interceptions_p90         NUMERIC(5,2),
    clearances_p90            NUMERIC(5,2),
    -- Creación y transición
    pass_accuracy_pct         NUMERIC(5,2),
    long_pass_accuracy_pct    NUMERIC(5,2),
    progressive_carries_p90   NUMERIC(5,2),
    passes_final_third_p90    NUMERIC(5,2),
    dribbles_successful_p90   NUMERIC(5,2),
    crosses_accurate_p90      NUMERIC(5,2),
    -- Portero (NULL para no-GK)
    saves_total               SMALLINT,
    save_pct                  NUMERIC(5,2),
    goals_prevented_xg        NUMERIC(5,2),
    -- Percentiles de liga (calculados en capa de procesamiento)
    percentile_league         JSONB,          -- {"xg_p90": 87, "duels_won_p90": 64, ...}
    created_at                TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_pss_source CHECK (source IN ('sofascore', 'fbref', 'fotmob')),
    UNIQUE (player_id, season_id, team_id, source)
);


-- -----------------------------------------------------------------------------
-- 10. PLAYER_MATCH_STATS — Estadísticas de jugador por partido (SofaScore)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_match_stats (
    id                    SERIAL PRIMARY KEY,
    player_id             INTEGER NOT NULL REFERENCES players(id),
    match_id              INTEGER NOT NULL REFERENCES matches(id),
    minutes_played        SMALLINT,
    rating                NUMERIC(4,2),     -- Ej. 7.43 (escala SofaScore 1-10)
    goals                 SMALLINT,
    assists               SMALLINT,
    yellow_cards          SMALLINT,
    red_cards             SMALLINT,
    shots_total           SMALLINT,
    shots_on_target       SMALLINT,
    key_passes            SMALLINT,
    duels_ground_won      SMALLINT,
    duels_aerial_won      SMALLINT,
    interceptions         SMALLINT,
    dribbles_successful   SMALLINT,
    pass_accuracy_pct     NUMERIC(5,2),
    heatmap_data          JSONB,            -- Array de coordenadas {x, y, intensity}
    UNIQUE (player_id, match_id)
);


-- -----------------------------------------------------------------------------
-- 11. PLAYER_MARKET_VALUES — Historial de valor de mercado (Transfermarkt)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_market_values (
    id             SERIAL PRIMARY KEY,
    player_id      INTEGER NOT NULL REFERENCES players(id),
    team_id        INTEGER REFERENCES teams(id),
    recorded_date  DATE NOT NULL,
    value_eur      INTEGER,                  -- Valor en euros
    UNIQUE (player_id, recorded_date)
);


-- -----------------------------------------------------------------------------
-- 12. TEAM_SEASON_STATS — Estadísticas de equipo por temporada
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS team_season_stats (
    id               SERIAL PRIMARY KEY,
    team_id          INTEGER NOT NULL REFERENCES teams(id),
    season_id        INTEGER NOT NULL REFERENCES seasons(id),
    source           VARCHAR(20) NOT NULL,
    matches_played   SMALLINT,
    wins             SMALLINT,
    draws            SMALLINT,
    losses           SMALLINT,
    goals_for        SMALLINT,
    goals_against    SMALLINT,
    xg_for           NUMERIC(6,2),
    xg_against       NUMERIC(6,2),
    shots_total      SMALLINT,
    shots_on_target  SMALLINT,
    big_chances      SMALLINT,
    key_passes       SMALLINT,
    interceptions    SMALLINT,
    form_last_5      VARCHAR(5),             -- Ej. "WWDLW" (W=victoria, D=empate, L=derrota)
    CONSTRAINT chk_tss_source CHECK (source IN ('sofascore', 'fbref', 'fotmob')),
    UNIQUE (team_id, season_id, source)
);


-- =============================================================================
-- ÍNDICES — Para consultas frecuentes esperadas
-- =============================================================================

-- Búsqueda de jugadores por nombre
CREATE INDEX IF NOT EXISTS idx_players_full_name        ON players(full_name);
-- Lookup de stats por jugador y temporada
CREATE INDEX IF NOT EXISTS idx_pss_player_season        ON player_season_stats(player_id, season_id);
-- Lookup de stats por partido
CREATE INDEX IF NOT EXISTS idx_pms_match                ON player_match_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_pms_player               ON player_match_stats(player_id);
-- Partidos por temporada y fecha
CREATE INDEX IF NOT EXISTS idx_matches_season_date      ON matches(season_id, match_date);
-- Historial de valor de mercado por jugador
CREATE INDEX IF NOT EXISTS idx_pmv_player_date          ON player_market_values(player_id, recorded_date);


-- =============================================================================
-- PERMISOS — Otorgar acceso a usuario de aplicación
-- =============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO cacique_app;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO cacique_app;
