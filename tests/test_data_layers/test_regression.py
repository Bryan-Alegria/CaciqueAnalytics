"""Regression tests for data layer refactoring.

Validates that the stat_registry, query builders, and refactored layers
produce the same JSON structure as before the refactor.
"""

import sys
sys.path.insert(0, "C:\\Users\\PC\\Projects\\CaciqueAnalytics")

import json
import unittest
from unittest.mock import MagicMock, patch

from src.data_layers import stat_registry
from src.data_layers import queries


class TestStatRegistry(unittest.TestCase):
    """Validate the unified stat registry."""

    def test_all_stats_have_metadata(self):
        for col in stat_registry.all_columns():
            meta = stat_registry.get(col)
            self.assertIsNotNone(meta.label)
            self.assertIsNotNone(meta.fmt)
            self.assertIsInstance(meta.higher_is_better, bool)

    def test_key_stats_subset_of_all(self):
        key = stat_registry.key_stats()
        all_cols = stat_registry.all_columns()
        for col in key:
            self.assertIn(col, all_cols)

    def test_comparison_stats_subset_of_all(self):
        comp = stat_registry.comparison_stats()
        all_cols = stat_registry.all_columns()
        for col in comp:
            self.assertIn(col, all_cols)

    def test_plain_text_tiers(self):
        # Elite tier
        self.assertIn("Elite", stat_registry.plain_text("goals", 95))
        # Destacado tier
        self.assertIn("Destacado", stat_registry.plain_text("rating", 87))
        # Promedio tier
        self.assertEqual(stat_registry.plain_text("assists", 50), "Promedio")
        # Por Debajo del Promedio
        self.assertEqual(stat_registry.plain_text("goals", 30), "Por Debajo del Promedio")

    def test_format_value(self):
        self.assertEqual(stat_registry.format_value("goals", 5), "5")
        self.assertEqual(stat_registry.format_value("rating", 7.234), "7.23")
        self.assertEqual(stat_registry.format_value("expected_goals", 3.1), "3.10")
        self.assertEqual(stat_registry.format_value("goals", None), "N/A")

    def test_higher_is_better_defaults_true(self):
        self.assertTrue(stat_registry.higher_is_better("goals"))
        self.assertFalse(stat_registry.higher_is_better("yellow_cards"))

    def test_leaderboard_stats_have_formats(self):
        for stat_def in stat_registry.leaderboard_stats():
            self.assertIsNotNone(stat_def.leaderboard_format)


class TestQueryBuilders(unittest.TestCase):
    """Validate reusable SQL query builders."""

    def test_player_season_base_includes_columns(self):
        sql = queries.player_season_base(["goals", "assists"])
        self.assertIn("goals, assists", sql)
        self.assertIn("FROM player_season_stats", sql)
        self.assertIn("LIMIT 1", sql)

    def test_player_season_base_parameterized(self):
        sql = queries.player_season_base(["rating"])
        self.assertIn("%s", sql)

    def test_player_identity_base_includes_all_fields(self):
        sql = queries.player_identity_base()
        self.assertIn("p.id AS player_id", sql)
        self.assertIn("pos.name_es AS position", sql)
        self.assertIn("t.name AS team_name", sql)
        self.assertIn("c.name AS competition_name", sql)


class TestRefactoredLayersStructure(unittest.TestCase):
    """Verify PlayerDataLayer and ComparisonDataLayer output structure."""

    def _mock_layer(self, layer_class, *args, **kwargs):
        """Instantiate a layer with mocked DB methods."""
        layer = layer_class(*args, **kwargs)
        layer.execute = MagicMock()
        layer.fetchone = MagicMock()
        layer.fetchall = MagicMock(return_value=[])
        return layer

    @patch("src.data_layers.player_layer.get_team_colors")
    @patch.object(stat_registry, "key_stats", return_value=["goals", "rating"])
    @patch("src.data_layers.player_layer.ContextEngine")
    def test_player_layer_structure(self, mock_ctx_class, mock_key_stats, mock_colors):
        mock_colors.return_value = {"primary": "#ff0000", "secondary": "#ffffff"}
        mock_ctx = MagicMock()
        mock_ctx.get_context.return_value = MagicMock(
            value=5, label="Goles", percentile=90,
            vs_average="+50% vs promedio", plain_text="Destacado",
            is_good_high=True
        )
        mock_ctx_class.return_value = mock_ctx

        layer = self._mock_layer(
            __import__("src.data_layers.player_layer", fromlist=["PlayerDataLayer"]).PlayerDataLayer,
            "Test Player", 2026, 1
        )
        layer.fetchone.side_effect = [
            (1, "Test Player", "Delantero", 10, "Colo-Colo", 2026, "Primera"),
            (10, 900, 5, 2, 1, 0),
            (5, 7.5),
        ]

        result = layer.build_layers()

        self.assertIn("layer_identity", result)
        self.assertIn("layer_basic_stats", result)
        self.assertIn("layer_key_stats", result)
        self.assertIn("layer_derived_stats", result)
        self.assertIn("layer_summary", result)

        identity = result["layer_identity"]
        self.assertEqual(identity["player_name"], "Test Player")
        self.assertEqual(identity["team"], "Colo-Colo")
        self.assertEqual(identity["team_colors"]["primary"], "#ff0000")

    @patch("src.data_layers.comparison_layer.get_team_colors")
    @patch.object(stat_registry, "comparison_stats", return_value=["goals", "rating"])
    def test_comparison_layer_structure(self, mock_comp, mock_colors):
        mock_colors.return_value = {"primary": "#ff0000", "secondary": "#ffffff"}

        layer = self._mock_layer(
            __import__("src.data_layers.comparison_layer", fromlist=["ComparisonDataLayer"]).ComparisonDataLayer,
            "Player A", "Player B", 2026, 1
        )
        layer.fetchone.side_effect = [
            (5, 7.5, 10, 900),  # Player A stats (goals, rating, matches, minutes)
            (3, 7.0, 10, 900),  # Player B stats
            (1, "Player A", "Delantero", 10, "Colo-Colo", 2026, "Primera"),
            (2, "Player B", "Mediocampista", 11, "U. Catolica", 2026, "Primera"),
        ]

        result = layer.build_layers()

        self.assertIn("layer_identity", result)
        self.assertIn("layer_summary", result)
        self.assertIn("layer_categories", result)
        self.assertIn("layer_basic_stats", result)

        self.assertEqual(result["layer_summary"]["headline"], "Player A vs Player B")
        self.assertIn("score", result["layer_summary"])

        categories = result["layer_categories"]
        self.assertTrue(len(categories) > 0)
        for cat in categories:
            self.assertIn("label", cat)
            self.assertIn("winner", cat)
            self.assertIn("is_higher_better", cat)


class TestLeaderboardLayerStructure(unittest.TestCase):
    """Verify LeaderboardDataLayer output structure."""

    def test_build_layers_has_identity(self):
        from src.data_layers.leaderboard_layer import LeaderboardDataLayer

        layer = LeaderboardDataLayer(2026, 1)
        layer.execute = MagicMock()
        layer.fetchall = MagicMock(return_value=[
            ("Player A", "Team A", 10, 10, 900),
            ("Player B", "Team B", 8, 10, 900),
        ])

        result = layer.build_layers()

        self.assertIn("layer_identity", result)
        identity = result["layer_identity"]
        self.assertEqual(identity["season"], 2026)
        self.assertEqual(identity["competition_id"], 1)

    def test_leaderboard_entry_structure(self):
        from src.data_layers.leaderboard_layer import LeaderboardDataLayer

        layer = LeaderboardDataLayer(2026, 1)
        layer.execute = MagicMock()
        layer.fetchall = MagicMock(return_value=[
            ("Player A", "Team A", 10, 10, 900),
        ])

        result = layer.build_layers()
        # Find the first leaderboard layer
        leaderboard_key = [k for k in result.keys() if k.startswith("layer_top_")][0]
        entries = result[leaderboard_key]
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertIn("rank", entry)
        self.assertIn("player_name", entry)
        self.assertIn("team", entry)
        self.assertIn("value", entry)
        self.assertIn("display_value", entry)


if __name__ == "__main__":
    unittest.main()
