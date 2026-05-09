"""Reusable SQL query builders for data layers."""


def player_season_base(columns: list[str]) -> str:
    """Build the standard player-season stats query.

    Returns a SELECT statement with the requested columns joined against
    players, seasons, and competitions. Callers must add WHERE clause
    parameters for player_name, year, and competition_id.
    """
    cols = ", ".join(columns) if columns else "*"
    return f"""
        SELECT {cols}
        FROM player_season_stats pss
        JOIN players p ON p.id = pss.player_id
        JOIN seasons s ON s.id = pss.season_id
        WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
        ORDER BY pss.minutes_played DESC
        LIMIT 1
    """.strip()


def player_identity_base() -> str:
    """Build the standard player identity query.

    Returns name, position, team, season, and competition info.
    Callers must add WHERE parameters for player_name, year, competition_id.
    """
    return """
        SELECT
            p.id AS player_id,
            p.full_name,
            pos.name_es AS position,
            t.id AS team_id,
            t.name AS team_name,
            s.year,
            c.name AS competition_name
        FROM player_season_stats pss
        JOIN players p ON p.id = pss.player_id
        LEFT JOIN positions pos ON pos.id = p.position_id
        JOIN teams t ON t.id = pss.team_id
        JOIN seasons s ON s.id = pss.season_id
        JOIN competitions c ON c.id = s.competition_id
        WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
        ORDER BY pss.minutes_played DESC
        LIMIT 1
    """.strip()
