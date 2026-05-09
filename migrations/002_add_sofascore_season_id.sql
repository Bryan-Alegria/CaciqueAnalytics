-- Migration: Add sofascore_season_id to seasons table
-- And populate known mappings

ALTER TABLE seasons ADD COLUMN sofascore_season_id INTEGER;

-- Populate known SofaScore season IDs
-- Primera Division 2026 = 88493, 2025 = 71131
UPDATE seasons SET sofascore_season_id = 88493 WHERE year = 2026 AND competition_id = 1;
UPDATE seasons SET sofascore_season_id = 71131 WHERE year = 2025 AND competition_id = 1;

-- Note: Other competitions (Copa de la Liga, Libertadores, Sudamericana)
-- will be populated when their season IDs are discovered.
