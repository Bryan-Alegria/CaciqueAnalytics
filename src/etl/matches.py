"""Match extraction and loading for the matches table."""

import logging
from datetime import datetime, timezone
from typing import Optional

from src.db.session import get_connection
from src.scraper.sofascore_client import SofaScoreClient

logger = logging.getLogger(__name__)


class MatchExtractor:
    """Fetch match fixtures from SofaScore and upsert into the matches table."""

    def __init__(self, client: Optional[SofaScoreClient] = None):
        self.client = client or SofaScoreClient()

    def fetch_fixtures(
        self,
        competition_id: int,
        season_id: int,
        round_number: Optional[int] = None,
    ) -> list[dict]:
        """Fetch match fixtures for a competition/season.

        Args:
            competition_id: Internal competition ID
            season_id: Internal season ID
            round_number: Specific round to fetch, or None for all rounds

        Returns:
            List of match dicts ready for upsert
        """
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT sofascore_id FROM competitions WHERE id = %s",
                (competition_id,),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                raise ValueError(f"Competition {competition_id} has no sofascore_id")
            tournament_id = row[0]

            cur.execute(
                "SELECT sofascore_season_id FROM seasons WHERE id = %s",
                (season_id,),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                raise ValueError(f"Season {season_id} has no sofascore_season_id")
            ss_season_id = row[0]
        finally:
            cur.close()
            conn.close()

        # Use a single browser session for all requests
        ss = self.client.client
        driver = ss._build_driver()
        try:
            # Fetch rounds
            rounds = self._fetch_rounds(tournament_id, ss_season_id, driver)
            if round_number is not None:
                rounds = [r for r in rounds if r == round_number]

            matches = []
            for r in rounds:
                logger.info(f"Fetching matches for round {r}")
                round_matches = self._fetch_round_matches(
                    tournament_id, ss_season_id, r, driver
                )
                matches.extend(round_matches)

            logger.info(f"Fetched {len(matches)} total matches")
            return matches
        finally:
            driver.quit()

    def _fetch_rounds(
        self, tournament_id: int, season_id: int, driver
    ) -> list[int]:
        """Return list of round numbers for a tournament/season."""
        path = f"api/v1/unique-tournament/{tournament_id}/season/{season_id}/rounds"
        data = self._fetch_with_driver(driver, path)
        rounds = data.get("rounds", [])
        return [r["round"] for r in rounds]

    def _fetch_round_matches(
        self, tournament_id: int, season_id: int, round_number: int, driver
    ) -> list[dict]:
        """Fetch matches for a specific round."""
        path = f"api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/round/{round_number}"
        data = self._fetch_with_driver(driver, path)
        events = data.get("events", [])

        matches = []
        for event in events:
            match = self._parse_event(event)
            if match:
                matches.append(match)

        return matches

    def _fetch_with_driver(self, driver, path: str) -> dict:
        """Make a single request through an existing driver session."""
        import json
        from bs4 import BeautifulSoup

        url = f"https://www.sofascore.com/{path}"
        driver.get(url)
        # Let the page load; SofaScore API responses are JSON embedded in HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return json.loads(soup.text)

    def _parse_event(self, event: dict) -> Optional[dict]:
        """Parse a SofaScore event into a match dict.

        Returns None if teams cannot be resolved.
        """
        home_team_ss_id = event.get("homeTeam", {}).get("id")
        away_team_ss_id = event.get("awayTeam", {}).get("id")

        home_team_id = self._resolve_team_id(home_team_ss_id)
        away_team_id = self._resolve_team_id(away_team_ss_id)

        if not home_team_id or not away_team_id:
            home_name = event.get("homeTeam", {}).get("name", "UNKNOWN")
            away_name = event.get("awayTeam", {}).get("name", "UNKNOWN")
            logger.warning(
                f"Could not resolve teams: {home_name} ({home_team_ss_id}) vs "
                f"{away_name} ({away_team_ss_id})"
            )
            return None

        status = event.get("status", {})
        status_type = status.get("type", "unknown")

        # Map SofaScore status to our status values
        status_map = {
            "finished": "finished",
            "inprogress": "live",
            "notstarted": "scheduled",
        }
        mapped_status = status_map.get(status_type, status_type)

        home_score = event.get("homeScore", {})
        away_score = event.get("awayScore", {})

        start_ts = event.get("startTimestamp")
        match_date = None
        if start_ts:
            match_date = datetime.fromtimestamp(start_ts, tz=timezone.utc)

        return {
            "sofascore_id": event.get("id"),
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "match_date": match_date,
            "home_score": home_score.get("current"),
            "away_score": away_score.get("current"),
            "home_ht_score": home_score.get("period1"),
            "away_ht_score": away_score.get("period1"),
            "status": mapped_status,
            "matchday": event.get("roundInfo", {}).get("round"),
            "source": "sofascore",
        }

    def _resolve_team_id(self, sofascore_id: Optional[int]) -> Optional[int]:
        """Map a SofaScore team ID to our internal team_id."""
        if not sofascore_id:
            return None

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM teams WHERE sofascore_id = %s",
                (sofascore_id,),
            )
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
            conn.close()

    def upsert_matches(self, matches: list[dict], season_id: int) -> dict:
        """Upsert matches into the database.

        Returns:
            Dict with counts: inserted, updated, skipped
        """
        if not matches:
            return {"inserted": 0, "updated": 0, "skipped": 0}

        conn = get_connection()
        cur = conn.cursor()

        inserted = updated = skipped = 0

        try:
            for match in matches:
                sofascore_id = match.get("sofascore_id")
                if not sofascore_id:
                    skipped += 1
                    continue

                # Check if exists
                cur.execute(
                    "SELECT id FROM matches WHERE sofascore_id = %s",
                    (sofascore_id,),
                )
                existing = cur.fetchone()

                columns = [
                    "season_id", "home_team_id", "away_team_id", "match_date",
                    "home_score", "away_score", "status", "matchday",
                    "sofascore_id", "home_ht_score", "away_ht_score", "source",
                ]

                values = [
                    season_id,
                    match["home_team_id"],
                    match["away_team_id"],
                    match.get("match_date"),
                    match.get("home_score"),
                    match.get("away_score"),
                    match.get("status"),
                    match.get("matchday"),
                    sofascore_id,
                    match.get("home_ht_score"),
                    match.get("away_ht_score"),
                    match.get("source", "sofascore"),
                ]

                if existing:
                    # Update only mutable fields
                    set_clause = ", ".join([
                        "home_score = %s",
                        "away_score = %s",
                        "status = %s",
                        "home_ht_score = %s",
                        "away_ht_score = %s",
                        "match_date = %s",
                    ])
                    cur.execute(
                        f"UPDATE matches SET {set_clause} WHERE id = %s",
                        [
                            match.get("home_score"),
                            match.get("away_score"),
                            match.get("status"),
                            match.get("home_ht_score"),
                            match.get("away_ht_score"),
                            match.get("match_date"),
                            existing[0],
                        ],
                    )
                    updated += 1
                else:
                    placeholders = ", ".join(["%s"] * len(columns))
                    cur.execute(
                        f"INSERT INTO matches ({', '.join(columns)}) VALUES ({placeholders})",
                        values,
                    )
                    inserted += 1

            conn.commit()
            logger.info(
                f"Matches upserted: {inserted} inserted, {updated} updated, {skipped} skipped"
            )

        except Exception as e:
            conn.rollback()
            logger.error(f"Match upsert failed: {e}")
            raise
        finally:
            cur.close()
            conn.close()

        return {"inserted": inserted, "updated": updated, "skipped": skipped}

    def run(self, competition_id: int, season_id: int, round_number: Optional[int] = None) -> dict:
        """Full extract + load for a competition/season.

        Returns:
            Dict with counts from upsert
        """
        matches = self.fetch_fixtures(competition_id, season_id, round_number)
        return self.upsert_matches(matches, season_id)
