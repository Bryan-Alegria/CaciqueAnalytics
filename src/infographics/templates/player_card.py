"""Player stat card infographic template."""

from pathlib import Path
from typing import Any

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch

from src.db.session import get_connection
from src.infographics.templates.base_template import BaseTemplate


class PlayerCard(BaseTemplate):
    """1080x1080 player stat card."""

    template_type = "player_card"

    def query(self, params: dict[str, Any]) -> pd.DataFrame:
        player_name = params["player_name"]
        season_year = params.get("season", 2026)
        competition_id = params.get("competition_id", 1)  # Default to Primera Chile

        conn = get_connection()
        query = """
            SELECT
                p.full_name AS player,
                t.name AS team,
                pss.goals,
                pss.assists,
                pss.rating,
                pss.minutes_played,
                pss.matches_played,
                pss.expected_goals,
                pss.shots_total,
                pss.shots_on_target,
                pss.key_passes_p90,
                pss.tackles_p90,
                pss.interceptions_p90,
                pss.pass_accuracy_pct,
                pss.yellow_cards,
                pss.red_cards
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN teams t ON t.id = pss.team_id
            JOIN seasons s ON s.id = pss.season_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
            LIMIT 1
        """
        df = pd.read_sql(query, conn, params=(player_name, season_year, competition_id))
        conn.close()
        return df

    def plot(self, data: pd.DataFrame) -> plt.Figure:
        if data.empty:
            raise ValueError("No data found for player card. Check player_name, season, and competition_id.")

        row = data.iloc[0]
        colors = self.style.colors
        team_colors = self.style.team_colors(row["team"])
        fonts = self.style.fonts

        fig = self.renderer.new_figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1080)
        ax.set_ylim(0, 1080)
        ax.axis("off")
        ax.set_facecolor(colors["background"])

        # Background accent bar at top
        accent_bar = FancyBboxPatch(
            (0, 1020), 1080, 60,
            boxstyle="square,pad=0",
            facecolor=team_colors["primary"],
            edgecolor="none",
        )
        ax.add_patch(accent_bar)

        # Player name
        ax.text(
            540, 990, row["player"],
            fontsize=fonts["title"]["size"],
            fontweight=fonts["title"]["weight"],
            color=colors["text_light"],
            ha="center", va="center",
            fontfamily=fonts["title"]["family"],
        )

        # Team name
        ax.text(
            540, 940, row["team"],
            fontsize=fonts["subtitle"]["size"],
            fontweight=fonts["subtitle"]["weight"],
            color=colors["accent"],
            ha="center", va="center",
            fontfamily=fonts["subtitle"]["family"],
        )

        # Stat grid
        stats = [
            ("Goals", row["goals"]),
            ("Assists", row["assists"]),
            ("Rating", f"{row['rating']:.2f}" if pd.notna(row["rating"]) else "N/A"),
            ("Minutes", int(row["minutes_played"]) if pd.notna(row["minutes_played"]) else "N/A"),
            ("Matches", int(row["matches_played"]) if pd.notna(row["matches_played"]) else "N/A"),
            ("xG", f"{row['expected_goals']:.2f}" if pd.notna(row["expected_goals"]) else "N/A"),
            ("Shots", int(row["shots_total"]) if pd.notna(row["shots_total"]) else "N/A"),
            ("SoT", int(row["shots_on_target"]) if pd.notna(row["shots_on_target"]) else "N/A"),
            ("Key Passes/90", f"{row['key_passes_p90']:.2f}" if pd.notna(row["key_passes_p90"]) else "N/A"),
            ("Tackles/90", f"{row['tackles_p90']:.2f}" if pd.notna(row["tackles_p90"]) else "N/A"),
            ("Interceptions/90", f"{row['interceptions_p90']:.2f}" if pd.notna(row["interceptions_p90"]) else "N/A"),
            ("Pass Acc %", f"{row['pass_accuracy_pct']:.1f}" if pd.notna(row["pass_accuracy_pct"]) else "N/A"),
        ]

        cols = 3
        start_y = 850
        cell_w = 1080 / cols
        cell_h = 180

        for i, (label, value) in enumerate(stats):
            c = i % cols
            r = i // cols
            x = c * cell_w + cell_w / 2
            y = start_y - r * cell_h

            # Card background
            card = FancyBboxPatch(
                (x - cell_w / 2 + 10, y - cell_h / 2 + 10),
                cell_w - 20, cell_h - 20,
                boxstyle="round,pad=5,rounding_size=10",
                facecolor=colors["surface"],
                edgecolor="none",
            )
            ax.add_patch(card)

            # Label
            ax.text(
                x, y + 25, label,
                fontsize=fonts["label"]["size"],
                fontweight=fonts["label"]["weight"],
                color=colors["text_muted"],
                ha="center", va="center",
                fontfamily=fonts["label"]["family"],
            )

            # Value
            ax.text(
                x, y - 15, str(value),
                fontsize=fonts["stat"]["size"],
                fontweight=fonts["stat"]["weight"],
                color=colors["text_light"],
                ha="center", va="center",
                fontfamily=fonts["stat"]["family"],
            )

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
        player = params["player_name"].replace(" ", "_")
        season = params.get("season", "2026")
        comp = params.get("competition_id", 1)
        return f"player_card_{player}_s{season}_c{comp}.png"
