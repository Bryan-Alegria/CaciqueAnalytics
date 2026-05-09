"""Tests for AutomationTrigger."""

import pytest

from src.automation.trigger import AutomationTrigger


class TestAutomationTrigger:
    """Tests for the automation trigger."""

    @pytest.fixture
    def trigger(self):
        return AutomationTrigger()

    def test_get_active_seasons_returns_list(self, trigger):
        """Should return a list of active season IDs."""
        seasons = trigger._get_active_seasons()
        assert isinstance(seasons, list)
        assert len(seasons) > 0

    def test_get_season_info_returns_dict(self, trigger):
        """Should return season metadata."""
        info = trigger._get_season_info(1)
        assert info is not None
        assert "id" in info
        assert "year" in info
        assert "competition_id" in info
        assert "competition_name" in info

    def test_get_season_info_invalid_returns_none(self, trigger):
        """Should return None for non-existent season."""
        info = trigger._get_season_info(99999)
        assert info is None

    def test_dry_run_returns_structure(self, trigger):
        """Dry run should return expected structure without side effects."""
        results = trigger.dry_run(season_ids=[1])
        assert "would_update_matches" in results
        assert "would_trigger_etl" in results
        assert "would_export" in results
        assert isinstance(results["would_update_matches"], list)
        assert isinstance(results["would_trigger_etl"], list)
        assert isinstance(results["would_export"], list)

    def test_run_returns_structure(self, trigger):
        """Run should return results structure."""
        results = trigger.run(season_ids=[1])
        assert "finished_matches" in results
        assert "etl_results" in results
        assert "completed_matchdays" in results
        assert "errors" in results
        assert isinstance(results["finished_matches"], list)
        assert isinstance(results["errors"], list)
