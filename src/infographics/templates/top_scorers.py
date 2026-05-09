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
        limit = params.get("limit", 10)

        conn = get_connection()
        query = """
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
            WHERE s.year = %s AND pss.goals IS NOT NULL
            ORDER BY pss.goals DESC
            LIMIT %s
        """
        df = pd.read_sql(query, conn, params=(season_year, limit))
        conn.close()
        return df

    def plot(self, data: pd.DataFrame) -> plt.Figure:
        if data.empty:
            raise ValueError("No data found for top scorers")

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
        ax.text(
            540, 940, f"Chile Primera Division {season}",
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
            stats_text = f"{int(row['goals'])} goals  |  {int(row['assists'])} assists  |  {row['rating']:.2f} rating"
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

        # Footer
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
        return f"top_scorers_{season}.png"
