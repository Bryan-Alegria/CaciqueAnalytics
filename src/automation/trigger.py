"""Automation trigger that orchestrates detection, ETL, and export."""

import logging
from datetime import datetime, timezone
from typing import Optional

from src.automation.detector import GamedayDetector
from src.automation.notifier import Notifier
from src.db.session import get_connection
from src.etl.matches import MatchExtractor

logger = logging.getLogger(__name__)


class AutomationTrigger:
    """Orchestrate the automation pipeline.

    Workflow:
    1. Detect newly finished matches
    2. Run ETL for affected competitions
    3. Check if matchday is complete
    4. Export data layers if complete
    5. Notify user
    """

    def __init__(
        self,
        detector: Optional[GamedayDetector] = None,
        notifier: Optional[Notifier] = None,
    ):
        self.detector = detector or GamedayDetector()
        self.notifier = notifier or Notifier()

    def run(
        self,
        competition_ids: Optional[list[int]] = None,
        season_ids: Optional[list[int]] = None,
    ) -> dict:
        """Run the full automation cycle.

        Args:
            competition_ids: List of competition IDs to check, or None for all
            season_ids: List of season IDs to check, or None for all active

        Returns:
            Dict with results of the run
        """
        logger.info("Starting automation cycle")
        results = {
            "finished_matches": [],
            "etl_results": [],
            "completed_matchdays": [],
            "errors": [],
        }

        # Determine which seasons to process
        seasons_to_process = season_ids or self._get_active_seasons(competition_ids)

        for season_id in seasons_to_process:
            try:
                season_results = self._process_season(season_id)
                results["finished_matches"].extend(season_results.get("finished_matches", []))
                results["etl_results"].extend(season_results.get("etl_results", []))
                results["completed_matchdays"].extend(season_results.get("completed_matchdays", []))
            except Exception as e:
                error_msg = f"Error processing season {season_id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                self.notifier.error(error_msg)

        logger.info("Automation cycle complete")
        return results

    def _process_season(self, season_id: int) -> dict:
        """Process a single season."""
        results = {
            "finished_matches": [],
            "etl_results": [],
            "completed_matchdays": [],
        }

        # Get season info
        season_info = self._get_season_info(season_id)
        if not season_info:
            logger.warning(f"Season {season_id} not found")
            return results

        competition_id = season_info["competition_id"]
        season_year = season_info["year"]
        competition_name = season_info["competition_name"]

        # 1. Update match data from SofaScore
        logger.info(f"Updating matches for season {season_id}")
        try:
            extractor = MatchExtractor()
            match_stats = extractor.run(competition_id, season_id)
            logger.info(f"Match update: {match_stats}")
        except Exception as e:
            logger.error(f"Failed to update matches: {e}")
            # Continue anyway - we might still have local data

        # 2. Check for newly finished matches
        newly_finished = self.detector.get_newly_finished()
        season_finished = [m for m in newly_finished if m["season_id"] == season_id]

        if season_finished:
            logger.info(
                f"Found {len(season_finished)} newly finished matches for season {season_id}"
            )
            results["finished_matches"].extend(season_finished)

            # 3. Check if any matchdays are now complete
            matchdays = set(m["matchday"] for m in season_finished)
            for matchday in matchdays:
                if self.detector.is_matchday_complete(matchday, season_id):
                    logger.info(
                        f"Matchday {matchday} complete for season {season_id}"
                    )
                    results["completed_matchdays"].append({
                        "matchday": matchday,
                        "season_id": season_id,
                        "competition_name": competition_name,
                        "season_year": season_year,
                    })
                    self.notifier.matchday_complete(
                        matchday, competition_name, season_year
                    )
        else:
            logger.info(f"No newly finished matches for season {season_id}")

        return results

    def _get_active_seasons(self, competition_ids: Optional[list[int]] = None) -> list[int]:
        """Return list of active season IDs.

        Active seasons are those marked as current or with unfinished matches.
        """
        conn = get_connection()
        cur = conn.cursor()

        try:
            if competition_ids:
                cur.execute(
                    """
                    SELECT id FROM seasons
                    WHERE is_current = true OR id IN (
                        SELECT DISTINCT season_id FROM matches
                        WHERE status != 'finished'
                    )
                    AND competition_id = ANY(%s)
                    """,
                    (competition_ids,),
                )
            else:
                cur.execute(
                    """
                    SELECT id FROM seasons
                    WHERE is_current = true OR id IN (
                        SELECT DISTINCT season_id FROM matches
                        WHERE status != 'finished'
                    )
                    """
                )

            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def _get_season_info(self, season_id: int) -> Optional[dict]:
        """Return season metadata."""
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT s.id, s.year, s.competition_id, c.name
                FROM seasons s
                JOIN competitions c ON s.competition_id = c.id
                WHERE s.id = %s
                """,
                (season_id,),
            )
            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "year": row[1],
                "competition_id": row[2],
                "competition_name": row[3],
            }
        finally:
            cur.close()
            conn.close()

    def dry_run(self, season_ids: Optional[list[int]] = None) -> dict:
        """Run without executing ETL or exports. Just report what would happen.

        Returns:
            Dict with predicted actions
        """
        logger.info("Starting dry run")
        results = {
            "would_update_matches": [],
            "would_trigger_etl": [],
            "would_export": [],
        }

        seasons_to_process = season_ids or self._get_active_seasons()

        for season_id in seasons_to_process:
            season_info = self._get_season_info(season_id)
            if not season_info:
                continue

            # Check for unfinished matches that might finish soon
            upcoming = self.detector.get_matches_by_status(
                "scheduled", season_id
            )
            today = datetime.now(timezone.utc).date()
            todays_matches = [
                m for m in upcoming
                if m.get("match_date") and m["match_date"].date() == today
            ]

            if todays_matches:
                results["would_update_matches"].append({
                    "season_id": season_id,
                    "matches_count": len(todays_matches),
                })

            # Check for recently finished matches
            recently_finished = self.detector.get_newly_finished()
            season_finished = [
                m for m in recently_finished if m["season_id"] == season_id
            ]

            if season_finished:
                matchdays = set(m["matchday"] for m in season_finished)
                for matchday in matchdays:
                    if self.detector.is_matchday_complete(matchday, season_id):
                        results["would_export"].append({
                            "season_id": season_id,
                            "matchday": matchday,
                            "competition": season_info["competition_name"],
                        })

        logger.info("Dry run complete")
        return results
