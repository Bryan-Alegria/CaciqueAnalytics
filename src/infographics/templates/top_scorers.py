"""Top scorers leaderboard infographic template."""

from typing import Any

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch

from src.db.session import get_connection
from src.infographics.templates.base_template import BaseTemplate


class TopScorers(BaseTemplate):
    """1080x1080 top scorers leaderboard."""

    template_type = "top_scorers"

    def query(self, params: dict[str, Any]) -> pd.DataFrame:
        season_year = params.get("season", 2026)
        competition_id = params.get("competition_id", 1)  # Default to Primera Chile
        limit = params.get("limit", 10)
        min_minutes = params.get("min_minutes", 270)  # 3 full matches minimum
        team_id = params.get("team_id")  # Optional: filter by specific team
        position_group = params.get("position_group")  # Optional: Goalkeepers, Defenders, Midfielders, Forwards

        conn = get_connection()

        # Build query dynamically
        where_clauses = [
            "s.year = %s",
            "s.competition_id = %s",
            "pss.minutes_played >= %s",
            "pss.goals IS NOT NULL"
        ]
        query_params = [season_year, competition_id, min_minutes]

        if team_id is not None:
            where_clauses.append("t.id = %s")
            query_params.append(team_id)

        if position_group is not None:
            where_clauses.append("pg.name = %s")
            query_params.append(position_group)

        query = f"""
            SELECT
                p.full_name AS player,
                t.name AS team,
                pss.goals,
                pss.assists,
                pss.rating,
                pss.matches_played
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN teams t ON t.id = pss.team_id
            JOIN seasons s ON s.id = pss.season_id
            LEFT JOIN player_team_seasons pts ON pts.player_id = p.id AND pts.season_id = s.id AND pts.team_id = t.id
            LEFT JOIN positions pg ON pg.id = pts.position_id
            WHERE {" AND ".join(where_clauses)}
            ORDER BY pss.goals DESC
            LIMIT %s
        """
        query_params.append(limit)

        df = pd.read_sql(query, conn, params=tuple(query_params))
        conn.close()
        
        # Get competition name for subtitle
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM competitions WHERE id = %s", (competition_id,))
        comp_row = cur.fetchone()
        cur.close()
        conn.close()
        
        df.attrs = {"season": season_year, "competition": comp_row[0] if comp_row else "Unknown"}
        return df

    def plot(self, data: pd.DataFrame) -> plt.Figure:
        if data.empty:
            raise ValueError("No data found for top scorers. Check filters (season, competition, min_minutes, team_id).")

        colors = self.style.colors
        fonts = self.style.fonts

        fig = self.renderer.new_figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1080)
        ax.set_ylim(0, 1080)
        ax.axis("off")
        ax.set_facecolor(colors["background"])

        # Title bar
        title_bar = FancyBboxPatch(
            (0, 1020), 1080, 60,
            boxstyle="square,pad=0",
            facecolor=colors["accent"],
            edgecolor="none",
        )
        ax.add_patch(title_bar)

        ax.text(
            540, 990, "TOP SCORERS",
            fontsize=fonts["title"]["size"],
            fontweight=fonts["title"]["weight"],
            color=colors["text_light"],
            ha="center", va="center",
            fontfamily=fonts["title"]["family"],
        )

        # Subtitle
        season = data.attrs.get("season", "2026") if hasattr(data, "attrs") else "2026"
        comp_name = data.attrs.get("competition", "Chile Primera Division") if hasattr(data, "attrs") else "Chile Primera Division"
        ax.text(
            540, 940, f"{comp_name} {season}",
            fontsize=fonts["subtitle"]["size"],
            fontweight=fonts["subtitle"]["weight"],
            color=colors["text_muted"],
            ha="center", va="center",
            fontfamily=fonts["subtitle"]["family"],
        )

        # Rows
        row_h = 75
        start_y = 880
        for i, row in data.iterrows():
            y = start_y - i * row_h
            rank = i + 1

            # Rank circle
            rank_color = colors["accent"] if rank <= 3 else colors["surface"]
            circle = plt.Circle((60, y), 25, color=rank_color, zorder=3)
            ax.add_patch(circle)
            ax.text(
                60, y, str(rank),
                fontsize=fonts["stat"]["size"],
                fontweight="bold",
                color=colors["text_light"],
                ha="center", va="center",
                zorder=4,
            )

            # Name
            ax.text(
                120, y + 12, row["player"],
                fontsize=fonts["body"]["size"] + 2,
                fontweight="bold",
                color=colors["text_light"],
                ha="left", va="center",
                fontfamily=fonts["body"]["family"],
            )

            # Team
            ax.text(
                120, y - 15, row["team"],
                fontsize=fonts["label"]["size"],
                color=colors["text_muted"],
                ha="left", va="center",
                fontfamily=fonts["label"]["family"],
            )

            # Stats
            goals = int(row['goals']) if pd.notna(row['goals']) else 0
            assists = int(row['assists']) if pd.notna(row['assists']) else 0
            rating = f"{row['rating']:.2f}" if pd.notna(row['rating']) else "N/A"
            stats_text = f"{goals} goals  |  {assists} assists  |  {rating} rating"
            ax.text(
                1050, y, stats_text,
                fontsize=fonts["body"]["size"],
                color=colors["text_light"],
                ha="right", va="center",
                fontfamily=fonts["body"]["family"],
            )

            # Divider
            if i < len(data) - 1:
                ax.plot([40, 1040], [y - row_h / 2, y - row_h / 2], color=colors["grid"], linewidth=1, alpha=0.5)

        # Footer with logo
        self._draw_logo(ax, x=60, y=30)
        ax.text(
            540, 30,
            "CaciqueAnalytics | Data via SofaScore",
            fontsize=fonts["label"]["size"],
            color=colors["text_muted"],
            ha="center", va="center",
            fontfamily=fonts["label"]["family"],
        )

        return fig

    def _filename(self, params: dict[str, Any]) -> str:
        season = params.get("season", "2026")
        comp = params.get("competition_id", 1)
        team = params.get("team_id", "")
        pos = params.get("position_group", "")
        suffix = f"c{comp}"
        if team:
            suffix += f"_t{team}"
        if pos:
            suffix += f"_{pos.lower()}"
        return f"top_scorers_{season}_{suffix}.png"
