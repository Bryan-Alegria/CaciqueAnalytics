"""Player similarity engine using nearest neighbors on stat vectors."""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from src.db.session import get_connection

logger = logging.getLogger(__name__)


@dataclass
class SimilarPlayer:
    """A player similar to the target."""

    player_id: int
    name: str
    team: str
    position_group: str
    similarity: float
    minutes_played: int
    matches_played: int


class SimilarityEngine:
    """Find players with similar statistical profiles.

    Uses cosine similarity on normalized per-90 stat vectors.
    """

    RAW_FEATURES = [
        "goals",
        "assists",
        "rating",
        "expected_goals",
        "shots_total",
        "shots_on_target",
        "pass_accuracy_pct",
        "key_passes_p90",
        "tackles_p90",
        "interceptions_p90",
        "clearances_p90",
        "dribbles_successful_p90",
        "duels_ground_won_p90",
        "duels_aerial_pct",
        "fouls_won_p90",
        "fouls_committed_p90",
        "accurate_crosses_p90",
        "long_pass_accuracy_pct",
        "offsides_p90",
    ]

    MIN_MINUTES = 270  # At least 3 full matches worth of minutes

    def __init__(self, season_year: int, competition_id: int):
        self.season_year = season_year
        self.competition_id = competition_id
        self.season_id: int | None = None
        self._df: pd.DataFrame | None = None
        self._scaler: StandardScaler | None = None
        self._vectors: np.ndarray | None = None
        self._resolve_season_id()
        self._fit()

    def _resolve_season_id(self) -> None:
        """Map season_year to internal season_id."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM seasons WHERE year = %s AND competition_id = %s",
                (self.season_year, self.competition_id),
            )
            row = cur.fetchone()
            if row:
                self.season_id = row[0]
            else:
                logger.warning(
                    f"No season found for year={self.season_year}, competition={self.competition_id}"
                )
        finally:
            cur.close()
            conn.close()

    def _fit(self) -> None:
        """Load data, compute per90, normalize, and cache vectors."""
        if self.season_id is None:
            logger.error("Cannot fit similarity engine: season_id not resolved")
            self._df = pd.DataFrame()
            self._vectors = np.array([])
            return

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    p.id AS player_id,
                    p.full_name AS name,
                    t.name AS team,
                    pg.position_group AS position_group,
                    pss.minutes_played,
                    pss.matches_played,
                    pss.goals,
                    pss.assists,
                    pss.rating,
                    pss.expected_goals,
                    pss.shots_total,
                    pss.shots_on_target,
                    pss.pass_accuracy_pct,
                    pss.key_passes_p90,
                    pss.tackles_p90,
                    pss.interceptions_p90,
                    pss.clearances_p90,
                    pss.dribbles_successful_p90,
                    pss.duels_ground_won_p90,
                    pss.duels_aerial_pct,
                    pss.fouls_won_p90,
                    pss.fouls_committed_p90,
                    pss.accurate_crosses_p90,
                    pss.long_pass_accuracy_pct,
                    pss.offsides_p90
                FROM player_season_stats pss
                JOIN players p ON pss.player_id = p.id
                JOIN teams t ON pss.team_id = t.id
                JOIN seasons s ON pss.season_id = s.id
                LEFT JOIN positions pg ON p.position_id = pg.id
                WHERE pss.season_id = %s AND s.competition_id = %s
                """,
                (self.season_id, self.competition_id),
            )
            # Note: the query above has a bug - s.competition_id should reference seasons table
            # Let me fix this
            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        if not rows:
            logger.warning("No player stats found for similarity engine")
            self._df = pd.DataFrame()
            self._vectors = np.array([])
            return

        columns = [
            "player_id", "name", "team", "position_group",
            "minutes_played", "matches_played",
            "goals", "assists", "rating", "expected_goals",
            "shots_total", "shots_on_target", "pass_accuracy_pct",
            "key_passes_p90", "tackles_p90", "interceptions_p90",
            "clearances_p90", "dribbles_successful_p90",
            "duels_ground_won_p90", "duels_aerial_pct",
            "fouls_won_p90", "fouls_committed_p90",
            "accurate_crosses_p90", "long_pass_accuracy_pct",
            "offsides_p90",
        ]
        df = pd.DataFrame(rows, columns=columns)

        # Filter: need minimum minutes to have meaningful per90 stats
        df = df[df["minutes_played"] >= self.MIN_MINUTES].copy()

        if df.empty:
            logger.warning("No players with sufficient minutes for similarity")
            self._df = df
            self._vectors = np.array([])
            return

        # Compute per90 for raw totals
        minutes = df["minutes_played"].replace(0, np.nan)
        df["goals_p90"] = df["goals"] / minutes * 90
        df["assists_p90"] = df["assists"] / minutes * 90
        df["shots_total_p90"] = df["shots_total"] / minutes * 90
        df["shots_on_target_p90"] = df["shots_on_target"] / minutes * 90

        # Select feature columns for vector
        feature_cols = [
            "goals_p90", "assists_p90", "rating", "expected_goals",
            "shots_total_p90", "shots_on_target_p90", "pass_accuracy_pct",
            "key_passes_p90", "tackles_p90", "interceptions_p90",
            "clearances_p90", "dribbles_successful_p90",
            "duels_ground_won_p90", "duels_aerial_pct",
            "fouls_won_p90", "fouls_committed_p90",
            "accurate_crosses_p90", "long_pass_accuracy_pct",
            "offsides_p90",
        ]

        # Handle missing values
        X = df[feature_cols].fillna(0)

        # Normalize
        self._scaler = StandardScaler()
        self._vectors = self._scaler.fit_transform(X)
        self._df = df.reset_index(drop=True)

        logger.info(
            f"Similarity engine fitted: {len(df)} players, {len(feature_cols)} features"
        )

    def find_similar(
        self,
        player_name: str,
        top_n: int = 5,
        same_position_only: bool = False,
    ) -> list[SimilarPlayer]:
        """Find the most similar players to a given player.

        Args:
            player_name: Full name of the target player
            top_n: Number of similar players to return
            same_position_only: If True, only compare within same position group

        Returns:
            List of SimilarPlayer sorted by similarity (descending)
        """
        if self._df is None or self._df.empty:
            logger.error("Similarity engine not fitted")
            return []

        # Find target player
        mask = self._df["name"].str.lower() == player_name.lower()
        if not mask.any():
            logger.error(f"Player not found: {player_name}")
            return []

        target_idx = mask.idxmax()
        target_row = self._df.iloc[target_idx]
        target_vector = self._vectors[target_idx].reshape(1, -1)

        # Filter by position if requested
        candidate_mask = ~mask  # Exclude self
        if same_position_only and pd.notna(target_row.get("position_group")):
            candidate_mask &= (
                self._df["position_group"] == target_row["position_group"]
            )

        candidate_indices = self._df[candidate_mask].index
        if len(candidate_indices) == 0:
            logger.warning("No candidates found with given filters")
            return []

        # Compute cosine similarity
        candidate_vectors = self._vectors[candidate_indices]
        similarities = cosine_similarity(target_vector, candidate_vectors)[0]

        # Build results
        results = []
        for idx, sim in zip(candidate_indices, similarities):
            row = self._df.iloc[idx]
            results.append(
                SimilarPlayer(
                    player_id=int(row["player_id"]),
                    name=row["name"],
                    team=row["team"],
                    position_group=row["position_group"] or "Unknown",
                    similarity=float(sim),
                    minutes_played=int(row["minutes_played"]),
                    matches_played=int(row["matches_played"]),
                )
            )

        # Sort by similarity descending
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:top_n]

    def get_player_vector(self, player_name: str) -> dict | None:
        """Return the normalized stat vector for a player.

        Useful for debugging or visualization.
        """
        if self._df is None or self._df.empty:
            return None

        mask = self._df["name"].str.lower() == player_name.lower()
        if not mask.any():
            return None

        idx = mask.idxmax()
        row = self._df.iloc[idx]
        vector = self._vectors[idx]

        feature_cols = [
            "goals_p90", "assists_p90", "rating", "expected_goals",
            "shots_total_p90", "shots_on_target_p90", "pass_accuracy_pct",
            "key_passes_p90", "tackles_p90", "interceptions_p90",
            "clearances_p90", "dribbles_successful_p90",
            "duels_ground_won_p90", "duels_aerial_pct",
            "fouls_won_p90", "fouls_committed_p90",
            "accurate_crosses_p90", "long_pass_accuracy_pct",
            "offsides_p90",
        ]

        return {
            "player": row["name"],
            "team": row["team"],
            "position": row["position_group"],
            "features": {col: float(val) for col, val in zip(feature_cols, vector)},
        }

    @property
    def player_count(self) -> int:
        """Number of players in the similarity index."""
        return len(self._df) if self._df is not None else 0
