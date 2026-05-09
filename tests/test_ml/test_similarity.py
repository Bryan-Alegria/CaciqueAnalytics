"""Tests for Player Similarity Engine."""

import pytest

from src.ml.similarity import SimilarityEngine


class TestSimilarityEngine:
    """Tests using real DB data."""

    @pytest.fixture
    def engine(self):
        return SimilarityEngine(season_year=2026, competition_id=1)

    def test_engine_fits_with_real_data(self, engine):
        """Should load and index real player data."""
        assert engine.player_count > 0
        assert engine.player_count >= 100

    def test_find_similar_returns_results(self, engine):
        """Should find similar players for a known striker."""
        similar = engine.find_similar("Fernando Zampedri", top_n=5)
        assert len(similar) > 0
        assert len(similar) <= 5
        for p in similar:
            assert p.name != "Fernando Zampedri"  # Self excluded
            assert 0 <= p.similarity <= 1
            assert p.minutes_played >= 270

    def test_find_similar_different_players(self, engine):
        """Should find different similars for different players."""
        sim_zampedri = engine.find_similar("Fernando Zampedri", top_n=3)
        sim_castro = engine.find_similar("Daniel Castro", top_n=3)

        zampedri_names = {p.name for p in sim_zampedri}
        castro_names = {p.name for p in sim_castro}

        # They should have at least some different results
        assert zampedri_names != castro_names

    def test_find_similar_unknown_player_returns_empty(self, engine):
        """Should return empty list for unknown player."""
        similar = engine.find_similar("Jugador Inexistente XYZ", top_n=5)
        assert similar == []

    def test_same_position_filter(self, engine):
        """Should return fewer results with same_position_only=True."""
        all_sim = engine.find_similar("Fernando Zampedri", top_n=10, same_position_only=False)
        pos_sim = engine.find_similar("Fernando Zampedri", top_n=10, same_position_only=True)

        # With position filter, we might get fewer or same count depending on data
        assert len(pos_sim) <= len(all_sim)

    def test_similarity_scores_descending(self, engine):
        """Results should be sorted by similarity descending."""
        similar = engine.find_similar("Fernando Zampedri", top_n=5)
        scores = [p.similarity for p in similar]
        assert scores == sorted(scores, reverse=True)

    def test_player_vector_returns_dict(self, engine):
        """Should return feature vector for a known player."""
        vec = engine.get_player_vector("Fernando Zampedri")
        assert vec is not None
        assert "features" in vec
        assert len(vec["features"]) > 0

    def test_player_vector_unknown_returns_none(self, engine):
        """Should return None for unknown player."""
        vec = engine.get_player_vector("Jugador Inexistente XYZ")
        assert vec is None

    def test_all_similar_players_have_required_fields(self, engine):
        """Each result should have all required fields."""
        similar = engine.find_similar("Fernando Zampedri", top_n=3)
        for p in similar:
            assert p.player_id > 0
            assert p.name
            assert p.team
            assert p.similarity >= 0
            assert p.minutes_played > 0
            assert p.matches_played > 0
