-- Migration: Add scrape_log table for ETL audit trail

CREATE TABLE IF NOT EXISTS scrape_log (
    id SERIAL PRIMARY KEY,
    run_started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    run_finished_at TIMESTAMP WITH TIME ZONE,
    source VARCHAR(20) NOT NULL,
    competition_id INTEGER REFERENCES competitions(id),
    season_id INTEGER REFERENCES seasons(id),
    position_group VARCHAR(5),
    records_fetched INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_skipped INTEGER,
    error_message TEXT,
    status VARCHAR(20) DEFAULT 'running',
    CONSTRAINT chk_scrape_log_status CHECK (
        status IN ('running', 'success', 'partial', 'failed')
    )
);

CREATE INDEX IF NOT EXISTS idx_scrape_log_run_started ON scrape_log (run_started_at);
CREATE INDEX IF NOT EXISTS idx_scrape_log_competition ON scrape_log (competition_id);
CREATE INDEX IF NOT EXISTS idx_scrape_log_status ON scrape_log (status);
