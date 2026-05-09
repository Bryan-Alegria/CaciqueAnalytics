"""Tests for MatchExtractor."""

from datetime import datetime, timezone

import pytest

from src.etl.matches import MatchExtractor


class TestMatchExtractorParsing:
    """Tests for match parsing logic (no live scraping)."""

    @pytest.fixture
    def extractor(self):
        return MatchExtractor()

    def test_parse_event_finished_match(self, extractor):
        """Should parse a finished match event."""
        event = {
            "id": 12345,
            "status": {"type": "finished"},
            "homeTeam": {"id": 3161, "name": "Universidad de Chile"},
            "awayTeam": {"id": 3162, "name": "Audax Italiano"},
            "startTimestamp": 1769814000,
            "roundInfo": {"round": 1},
            "homeScore": {"current": 2, "period1": 1},
            "awayScore": {"current": 1, "period1": 0},
        }

        result = extractor._parse_event(event)
        assert result is not None
        assert result["sofascore_id"] == 12345
        assert result["status"] == "finished"
        assert result["home_score"] == 2
        assert result["away_score"] == 1
        assert result["home_ht_score"] == 1
        assert result["away_ht_score"] == 0
        assert result["matchday"] == 1
        assert result["match_date"] == datetime.fromtimestamp(1769814000, tz=timezone.utc)

    def test_parse_event_scheduled_match(self, extractor):
        """Should parse a scheduled match event."""
        event = {
            "id": 12346,
            "status": {"type": "notstarted"},
            "homeTeam": {"id": 3155, "name": "Colo-Colo"},
            "awayTeam": {"id": 3151, "name": "Universidad Catolica"},
            "startTimestamp": 1772492400,
            "roundInfo": {"round": 5},
            "homeScore": {},
            "awayScore": {},
        }

        result = extractor._parse_event(event)
        assert result is not None
        assert result["status"] == "scheduled"
        assert result["home_score"] is None
        assert result["away_score"] is None

    def test_parse_event_unknown_team_returns_none(self, extractor):
        """Should return None if team cannot be resolved."""
        event = {
            "id": 12347,
            "status": {"type": "finished"},
            "homeTeam": {"id": 99999, "name": "Unknown Team"},
            "awayTeam": {"id": 3162, "name": "Audax Italiano"},
            "startTimestamp": 1769814000,
            "roundInfo": {"round": 1},
            "homeScore": {"current": 0},
            "awayScore": {"current": 0},
        }

        result = extractor._parse_event(event)
        assert result is None

    def test_parse_event_live_match(self, extractor):
        """Should parse a live match event."""
        event = {
            "id": 12348,
            "status": {"type": "inprogress"},
            "homeTeam": {"id": 3161, "name": "Universidad de Chile"},
            "awayTeam": {"id": 3162, "name": "Audax Italiano"},
            "startTimestamp": 1769814000,
            "roundInfo": {"round": 1},
            "homeScore": {"current": 1},
            "awayScore": {"current": 0},
        }

        result = extractor._parse_event(event)
        assert result is not None
        assert result["status"] == "live"


class TestMatchExtractorUpsert:
    """Tests for match upsert logic."""

    @pytest.fixture
    def extractor(self):
        return MatchExtractor()

    def test_upsert_empty_list(self, extractor):
        """Should handle empty match list."""
        stats = extractor.upsert_matches([], season_id=1)
        assert stats == {"inserted": 0, "updated": 0, "skipped": 0}

    def test_upsert_matches_resolves_team(self, extractor):
        """Should resolve team ID from sofascore_id."""
        team_id = extractor._resolve_team_id(3161)
        assert team_id is not None
        assert isinstance(team_id, int)

    def test_upsert_matches_unknown_team_returns_none(self, extractor):
        """Should return None for unknown team."""
        team_id = extractor._resolve_team_id(99999)
        assert team_id is None
