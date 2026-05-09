"""Gameday detection logic."""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from src.db.session import get_connection

logger = logging.getLogger(__name__)


class GamedayDetector:
    """Detect matchdays, status changes, and completion."""

    def get_today_matches(self, season_id: Optional[int] = None) -> list[dict]:
        """Return matches scheduled for today.

        Args:
            season_id: Filter by season, or None for all seasons

        Returns:
            List of match dicts
        """
        today = date.today()
        return self.get_matches_for_date(today, season_id)

    def get_matches_for_date(
        self, target_date: date, season_id: Optional[int] = None
    ) -> list[dict]:
        """Return matches scheduled for a specific date."""
        conn = get_connection()
        cur = conn.cursor()

        try:
            query = """
                SELECT m.id, m.sofascore_id, m.matchday, m.status,
                       m.match_date, m.home_score, m.away_score,
                       ht.name as home_team, at.name as away_team,
                       s.year as season_year, c.name as competition_name
                FROM matches m
                JOIN teams ht ON m.home_team_id = ht.id
                JOIN teams at ON m.away_team_id = at.id
                JOIN seasons s ON m.season_id = s.id
                JOIN competitions c ON s.competition_id = c.id
                WHERE m.match_date::date = %s
            """
            params = [target_date]

            if season_id is not None:
                query += " AND m.season_id = %s"
                params.append(season_id)

            query += " ORDER BY m.match_date"

            cur.execute(query, params)
            rows = cur.fetchall()

            matches = []
            for row in rows:
                matches.append({
                    "id": row[0],
                    "sofascore_id": row[1],
                    "matchday": row[2],
                    "status": row[3],
                    "match_date": row[4],
                    "home_score": row[5],
                    "away_score": row[6],
                    "home_team": row[7],
                    "away_team": row[8],
                    "season_year": row[9],
                    "competition_name": row[10],
                })

            return matches
        finally:
            cur.close()
            conn.close()

    def get_matches_by_status(
        self, status: str, season_id: Optional[int] = None
    ) -> list[dict]:
        """Return matches with a specific status."""
        conn = get_connection()
        cur = conn.cursor()

        try:
            query = """
                SELECT m.id, m.sofascore_id, m.matchday, m.status,
                       m.match_date, m.home_score, m.away_score,
                       ht.name as home_team, at.name as away_team
                FROM matches m
                JOIN teams ht ON m.home_team_id = ht.id
                JOIN teams at ON m.away_team_id = at.id
                WHERE m.status = %s
            """
            params = [status]

            if season_id is not None:
                query += " AND m.season_id = %s"
                params.append(season_id)

            query += " ORDER BY m.match_date"

            cur.execute(query, params)
            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "sofascore_id": row[1],
                    "matchday": row[2],
                    "status": row[3],
                    "match_date": row[4],
                    "home_score": row[5],
                    "away_score": row[6],
                    "home_team": row[7],
                    "away_team": row[8],
                }
                for row in rows
            ]
        finally:
            cur.close()
            conn.close()

    def check_status_changes(
        self, since: Optional[datetime] = None
    ) -> list[dict]:
        """Detect matches whose status changed recently.

        For now, this queries matches that are 'live' or recently 'finished'.
        A more robust implementation would compare against a previous snapshot.

        Args:
            since: Only check matches updated after this timestamp

        Returns:
            List of matches with changed status
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(hours=6)

        conn = get_connection()
        cur = conn.cursor()

        try:
            # Matches that finished or went live recently
            # We approximate by looking at matches scheduled for today
            # that now have a different status
            cur.execute(
                """
                SELECT m.id, m.sofascore_id, m.matchday, m.status,
                       m.match_date, m.home_score, m.away_score,
                       ht.name as home_team, at.name as away_team
                FROM matches m
                JOIN teams ht ON m.home_team_id = ht.id
                JOIN teams at ON m.away_team_id = at.id
                WHERE m.match_date >= %s
                  AND m.status IN ('live', 'finished')
                ORDER BY m.match_date
                """,
                (since,),
            )
            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "sofascore_id": row[1],
                    "matchday": row[2],
                    "status": row[3],
                    "match_date": row[4],
                    "home_score": row[5],
                    "away_score": row[6],
                    "home_team": row[7],
                    "away_team": row[8],
                }
                for row in rows
            ]
        finally:
            cur.close()
            conn.close()

    def get_newly_finished(
        self, since: Optional[datetime] = None
    ) -> list[dict]:
        """Return matches that finished since the given time.

        Args:
            since: Lookback window. Defaults to 6 hours ago.

        Returns:
            List of finished match dicts
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(hours=6)

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT m.id, m.sofascore_id, m.matchday, m.status,
                       m.match_date, m.home_score, m.away_score,
                       ht.name as home_team, at.name as away_team,
                       s.id as season_id, c.id as competition_id
                FROM matches m
                JOIN teams ht ON m.home_team_id = ht.id
                JOIN teams at ON m.away_team_id = at.id
                JOIN seasons s ON m.season_id = s.id
                JOIN competitions c ON s.competition_id = c.id
                WHERE m.status = 'finished'
                  AND m.match_date >= %s
                ORDER BY m.match_date
                """,
                (since,),
            )
            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "sofascore_id": row[1],
                    "matchday": row[2],
                    "status": row[3],
                    "match_date": row[4],
                    "home_score": row[5],
                    "away_score": row[6],
                    "home_team": row[7],
                    "away_team": row[8],
                    "season_id": row[9],
                    "competition_id": row[10],
                }
                for row in rows
            ]
        finally:
            cur.close()
            conn.close()

    def is_matchday_complete(
        self, matchday: int, season_id: int
    ) -> bool:
        """Check if all matches in a matchday have status 'finished'.

        Args:
            matchday: The matchday/round number
            season_id: Internal season ID

        Returns:
            True if all matches are finished, False otherwise
        """
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT status FROM matches
                WHERE matchday = %s AND season_id = %s
                """,
                (matchday, season_id),
            )
            statuses = [row[0] for row in cur.fetchall()]

            if not statuses:
                logger.warning(
                    f"No matches found for matchday {matchday}, season {season_id}"
                )
                return False

            return all(s == "finished" for s in statuses)
        finally:
            cur.close()
            conn.close()

    def get_current_matchday(self, season_id: int) -> Optional[int]:
        """Return the current matchday based on finished matches.

        This returns the highest matchday that has at least one finished match.
        """
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT MAX(matchday) FROM matches
                WHERE season_id = %s AND status = 'finished'
                """,
                (season_id,),
            )
            row = cur.fetchone()
            return row[0] if row and row[0] else None
        finally:
            cur.close()
            conn.close()

    def get_upcoming_matchdays(
        self, season_id: int, limit: int = 3
    ) -> list[int]:
        """Return upcoming matchdays that have scheduled matches.

        Args:
            season_id: Internal season ID
            limit: Maximum number of matchdays to return

        Returns:
            List of matchday numbers
        """
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT DISTINCT matchday FROM matches
                WHERE season_id = %s AND status = 'scheduled'
                ORDER BY matchday
                LIMIT %s
                """,
                (season_id, limit),
            )
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()
