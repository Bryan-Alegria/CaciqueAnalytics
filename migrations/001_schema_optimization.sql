-- Migration: Phase 1 DB Schema Optimization
-- Date: 2026-05-09
-- Description: Add missing columns, indexes, and new tables based on SofaScore data shapes

-- 1.1 Fix teams table -- missing fotmob_id
ALTER TABLE teams ADD COLUMN IF NOT EXISTS fotmob_id INTEGER;
ALTER TABLE teams DROP CONSTRAINT IF EXISTS teams_fotmob_id_key;
ALTER TABLE teams ADD CONSTRAINT teams_fotmob_id_key UNIQUE (fotmob_id);
CREATE INDEX IF NOT EXISTS idx_teams_fotmob_id ON teams (fotmob_id) WHERE fotmob_id IS NOT NULL;

-- 1.2 Fix competitions table -- missing transfermarkt_id
ALTER TABLE competitions ADD COLUMN IF NOT EXISTS transfermarkt_id INTEGER;
ALTER TABLE competitions DROP CONSTRAINT IF EXISTS competitions_transfermarkt_id_key;
ALTER TABLE competitions ADD CONSTRAINT competitions_transfermarkt_id_key UNIQUE (transfermarkt_id);
CREATE INDEX IF NOT EXISTS idx_competitions_transfermarkt_id ON competitions (transfermarkt_id) WHERE transfermarkt_id IS NOT NULL;

-- 1.3 Extend player_season_stats -- SofaScore fields not yet covered
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS tackles_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS rating NUMERIC(4,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS expected_goals NUMERIC(6,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS big_chances_missed SMALLINT;
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS fouls_won_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS fouls_committed_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS accurate_crosses_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS long_pass_accuracy_pct NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS offsides_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS hit_woodwork SMALLINT;
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS shots_blocked SMALLINT;
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS dispossessed_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS dribbled_past_p90 NUMERIC(5,2);
ALTER TABLE player_season_stats ADD COLUMN IF NOT EXISTS shot_conversion_pct NUMERIC(5,2);

-- 1.4 Extend player_match_stats -- match-level fields
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS sub_on_min SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS sub_off_min SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS expected_goals NUMERIC(5,2);
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS expected_assists NUMERIC(5,2);
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS fouls_won SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS fouls_committed SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS offsides SMALLINT;
ALTER TABLE player_match_stats ADD COLUMN IF NOT EXISTS was_fouled SMALLINT;

-- 1.5 Extend team_season_stats -- team-level aggregates
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS clean_sheets SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS failed_to_score SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS possession_avg NUMERIC(5,2);
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS yellow_cards SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS red_cards SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS corners SMALLINT;
ALTER TABLE team_season_stats ADD COLUMN IF NOT EXISTS fouls_committed SMALLINT;

-- 1.6 Extend matches -- match context fields
ALTER TABLE matches ADD COLUMN IF NOT EXISTS home_ht_score SMALLINT;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS away_ht_score SMALLINT;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS referee CHARACTER VARYING(100);
ALTER TABLE matches ADD COLUMN IF NOT EXISTS venue CHARACTER VARYING(150);
ALTER TABLE matches ADD COLUMN IF NOT EXISTS attendance INTEGER;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS source CHARACTER VARYING(20);

-- 1.7 Add seasons.is_current flag
ALTER TABLE seasons ADD COLUMN IF NOT EXISTS is_current BOOLEAN DEFAULT false;

-- 1.8 New table: match_team_stats
CREATE TABLE IF NOT EXISTS match_team_stats (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id),
    team_id INTEGER NOT NULL REFERENCES teams(id),
    possession_pct NUMERIC(5,2),
    shots_total SMALLINT,
    shots_on_target SMALLINT,
    corners SMALLINT,
    fouls SMALLINT,
    yellow_cards SMALLINT,
    red_cards SMALLINT,
    offsides SMALLINT,
    passes_total SMALLINT,
    passes_accurate SMALLINT,
    pass_accuracy_pct NUMERIC(5,2),
    xg NUMERIC(5,2),
    big_chances SMALLINT,
    hit_woodwork SMALLINT,
    CONSTRAINT match_team_stats_match_team_key UNIQUE (match_id, team_id)
);
CREATE INDEX IF NOT EXISTS idx_mts_match ON match_team_stats (match_id);
CREATE INDEX IF NOT EXISTS idx_mts_team ON match_team_stats (team_id);

-- 1.9 New table: standings
CREATE TABLE IF NOT EXISTS standings (
    id SERIAL PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES seasons(id),
    matchday SMALLINT NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    position SMALLINT NOT NULL,
    points SMALLINT NOT NULL,
    played SMALLINT DEFAULT 0,
    wins SMALLINT DEFAULT 0,
    draws SMALLINT DEFAULT 0,
    losses SMALLINT DEFAULT 0,
    goals_for SMALLINT DEFAULT 0,
    goals_against SMALLINT DEFAULT 0,
    goal_difference SMALLINT DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT standings_season_matchday_team_key UNIQUE (season_id, matchday, team_id)
);
CREATE INDEX IF NOT EXISTS idx_standings_season_matchday ON standings (season_id, matchday);
CREATE INDEX IF NOT EXISTS idx_standings_team ON standings (team_id);

-- 1.10 New table: scrape_log
CREATE TABLE IF NOT EXISTS scrape_log (
    id SERIAL PRIMARY KEY,
    run_started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    run_finished_at TIMESTAMP WITH TIME ZONE,
    source CHARACTER VARYING(20) NOT NULL,
    competition_id INTEGER REFERENCES competitions(id),
    season_id INTEGER REFERENCES seasons(id),
    position_group CHARACTER VARYING(5),
    records_fetched INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_skipped INTEGER,
    error_message TEXT,
    status CHARACTER VARYING(20) DEFAULT 'running'
);
CREATE INDEX IF NOT EXISTS idx_scrape_log_run_started ON scrape_log (run_started_at);
CREATE INDEX IF NOT EXISTS idx_scrape_log_competition ON scrape_log (competition_id);
CREATE INDEX IF NOT EXISTS idx_scrape_log_status ON scrape_log (status);

-- 1.11 New table: infographics_log
CREATE TABLE IF NOT EXISTS infographics_log (
    id SERIAL PRIMARY KEY,
    type CHARACTER VARYING(50) NOT NULL,
    title CHARACTER VARYING(200),
    season_id INTEGER REFERENCES seasons(id),
    matchday SMALLINT,
    player_ids INTEGER[],
    team_ids INTEGER[],
    file_path CHARACTER VARYING(500),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status CHARACTER VARYING(20) DEFAULT 'draft'
);

-- 1.12 Add missing indexes
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches (status) WHERE status = 'scheduled';
CREATE INDEX IF NOT EXISTS idx_matches_matchday ON matches (matchday);
