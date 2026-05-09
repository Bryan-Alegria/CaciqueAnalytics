"""Player comparison infographic template."""

from typing import Any

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch

from src.db.session import get_connection
from src.infographics.templates.base_template import BaseTemplate


class PlayerComparison(BaseTemplate):
    """1080x1080 head-to-head player comparison card."""

    template_type = "player_comparison"

    def query(self, params: dict[str, Any]) -> pd.DataFrame:
        player_a = params["player_a"]
        player_b = params["player_b"]
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
            WHERE p.full_name = ANY(%s) AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
        """
        df = pd.read_sql(query, conn, params=([player_a, player_b], season_year, competition_id))
        conn.close()

        # Validate: must have exactly 2 unique players
        if len(df) == 0:
            raise ValueError(f"No data found for either player. Check player names, season, and competition_id.")
        
        unique_players = df["player"].unique()
        if len(unique_players) < 2:
            found = unique_players[0] if len(unique_players) > 0 else "none"
            missing = player_a if found == player_b else player_b
            raise ValueError(f"Player '{missing}' not found. Only found '{found}'.")
        
        # Deduplicate: if a player has multiple team records for same competition, pick the one with most minutes
        df = df.sort_values("minutes_played", ascending=False).drop_duplicates(subset=["player"], keep="first")
        
        return df

    def plot(self, data: pd.DataFrame) -> plt.Figure:
        if len(data) != 2:
            raise ValueError(f"Need exactly 2 players for comparison, got {len(data['player'].unique())}")

        colors = self.style.colors
        fonts = self.style.fonts

        fig = self.renderer.new_figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1080)
        ax.set_ylim(0, 1080)
        ax.axis("off")
        ax.set_facecolor(colors["background"])

        row_a = data.iloc[0]
        row_b = data.iloc[1]
        team_a_colors = self.style.team_colors(row_a["team"])
        team_b_colors = self.style.team_colors(row_b["team"])

        # Title
        title_bar = FancyBboxPatch(
            (0, 1020), 1080, 60,
            boxstyle="square,pad=0",
            facecolor=colors["accent"],
            edgecolor="none",
        )
        ax.add_patch(title_bar)
        ax.text(
            540, 990, "PLAYER COMPARISON",
            fontsize=fonts["title"]["size"],
            fontweight=fonts["title"]["weight"],
            color=colors["text_light"],
            ha="center", va="center",
            fontfamily=fonts["title"]["family"],
        )

        # Player names and teams
        ax.text(
            270, 940, row_a["player"],
            fontsize=fonts["subtitle"]["size"],
            fontweight="bold",
            color=team_a_colors["primary"],
            ha="center", va="center",
            fontfamily=fonts["subtitle"]["family"],
        )
        ax.text(
            270, 905, row_a["team"],
            fontsize=fonts["label"]["size"],
            color=colors["text_muted"],
            ha="center", va="center",
            fontfamily=fonts["label"]["family"],
        )

        ax.text(
            810, 940, row_b["player"],
            fontsize=fonts["subtitle"]["size"],
            fontweight="bold",
            color=team_b_colors["primary"],
            ha="center", va="center",
            fontfamily=fonts["subtitle"]["family"],
        )
        ax.text(
            810, 905, row_b["team"],
            fontsize=fonts["label"]["size"],
            color=colors["text_muted"],
            ha="center", va="center",
            fontfamily=fonts["label"]["family"],
        )

        # VS badge
        vs_circle = plt.Circle((540, 922), 22, color=colors["surface"], zorder=3)
        ax.add_patch(vs_circle)
        ax.text(
            540, 922, "VS",
            fontsize=fonts["stat"]["size"],
            fontweight="bold",
            color=colors["text_light"],
            ha="center", va="center",
            zorder=4,
        )

        # Stats to compare
        stats = [
            ("Goals", "goals"),
            ("Assists", "assists"),
            ("Rating", "rating", lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            ("Minutes", "minutes_played", lambda v: f"{int(v)}" if pd.notna(v) else "N/A"),
            ("Matches", "matches_played", lambda v: f"{int(v)}" if pd.notna(v) else "N/A"),
            ("xG", "expected_goals", lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            ("Shots", "shots_total", lambda v: f"{int(v)}" if pd.notna(v) else "N/A"),
            ("SoT", "shots_on_target", lambda v: f"{int(v)}" if pd.notna(v) else "N/A"),
            ("Key Passes/90", "key_passes_p90", lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            ("Pass Acc %", "pass_accuracy_pct", lambda v: f"{v:.1f}" if pd.notna(v) else "N/A"),
        ]

        row_h = 70
        start_y = 850
        for i, stat_def in enumerate(stats):
            label = stat_def[0]
            col = stat_def[1]
            fmt = stat_def[2] if len(stat_def) > 2 else lambda v: f"{int(v)}" if pd.notna(v) else "N/A"

            y = start_y - i * row_h
            val_a = fmt(row_a[col])
            val_b = fmt(row_b[col])

            # Determine winner for highlighting
            try:
                num_a = float(row_a[col]) if pd.notna(row_a[col]) else None
                num_b = float(row_b[col]) if pd.notna(row_b[col]) else None
            except (ValueError, TypeError):
                num_a = num_b = None

            color_a = colors["success"] if num_a is not None and num_b is not None and num_a > num_b else colors["text_light"]
            color_b = colors["success"] if num_a is not None and num_b is not None and num_b > num_a else colors["text_light"]

            # Label
            ax.text(
                540, y + 18, label,
                fontsize=fonts["label"]["size"],
                color=colors["text_muted"],
                ha="center", va="center",
                fontfamily=fonts["label"]["family"],
            )

            # Value A
            ax.text(
                270, y - 12, str(val_a),
                fontsize=fonts["stat"]["size"],
                fontweight="bold",
                color=color_a,
                ha="center", va="center",
                fontfamily=fonts["stat"]["family"],
            )

            # Value B
            ax.text(
                810, y - 12, str(val_b),
                fontsize=fonts["stat"]["size"],
                fontweight="bold",
                color=color_b,
                ha="center", va="center",
                fontfamily=fonts["stat"]["family"],
            )

            # Divider
            if i < len(stats) - 1:
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
        a = params["player_a"].replace(" ", "_")
        b = params["player_b"].replace(" ", "_")
        season = params.get("season", "2026")
        comp = params.get("competition_id", 1)
        return f"player_comparison_{a}_vs_{b}_s{season}_c{comp}.png"
