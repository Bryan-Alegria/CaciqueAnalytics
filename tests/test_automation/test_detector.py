"""Tests for GamedayDetector."""

import pytest

from src.automation.detector import GamedayDetector


class TestGamedayDetector:
    """Tests using the real matches table data."""

    @pytest.fixture
    def detector(self):
        return GamedayDetector()

    def test_get_matches_by_status_finished(self, detector):
        """Should return finished matches."""
        finished = detector.get_matches_by_status("finished", season_id=1)
        assert len(finished) > 0
        for match in finished:
            assert match["status"] == "finished"

    def test_get_matches_by_status_scheduled(self, detector):
        """Should return scheduled matches."""
        scheduled = detector.get_matches_by_status("scheduled", season_id=1)
        assert len(scheduled) > 0
        for match in scheduled:
            assert match["status"] == "scheduled"

    def test_is_matchday_complete_true(self, detector):
        """Matchday 1 should be complete (all matches finished)."""
        assert detector.is_matchday_complete(1, season_id=1) is True

    def test_is_matchday_complete_false(self, detector):
        """A future matchday should not be complete."""
        # Matchday 10 should have scheduled matches
        scheduled = detector.get_matches_by_status("scheduled", season_id=1)
        if scheduled:
            future_matchday = scheduled[0]["matchday"]
            assert detector.is_matchday_complete(future_matchday, season_id=1) is False

    def test_get_current_matchday(self, detector):
        """Should return the highest finished matchday."""
        current = detector.get_current_matchday(season_id=1)
        assert current is not None
        assert current >= 1

    def test_get_upcoming_matchdays(self, detector):
        """Should return upcoming matchdays with scheduled matches."""
        upcoming = detector.get_upcoming_matchdays(season_id=1, limit=3)
        assert len(upcoming) > 0
        assert all(isinstance(md, int) for md in upcoming)

    def test_get_newly_finished_returns_list(self, detector):
        """Should return a list (may be empty if no recent matches)."""
        finished = detector.get_newly_finished()
        assert isinstance(finished, list)

    def test_today_matches_returns_list(self, detector):
        """Should return a list (may be empty if no matches today)."""
        today = detector.get_today_matches(season_id=1)
        assert isinstance(today, list)
