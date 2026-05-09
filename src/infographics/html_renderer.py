"""HTML-based infographic renderer using Playwright."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import jinja2
from playwright.sync_api import sync_playwright

from src.db.session import get_connection

# Resolve template dir
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "html"
CSS_DIR = Path(__file__).resolve().parent / "templates" / "css"
ASSETS_DIR = Path(__file__).resolve().parent / "templates" / "assets"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "Infographics"


class HTMLRenderer:
    """Render HTML templates to PNG using Playwright."""

    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([str(TEMPLATE_DIR), str(CSS_DIR), str(ASSETS_DIR)]),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
        self.css_cache: dict[str, str] = {}
        self._load_css()

    def _load_css(self):
        """Pre-load CSS files into cache."""
        for css_file in CSS_DIR.glob("*.css"):
            self.css_cache[css_file.name] = css_file.read_text(encoding="utf-8")

    def render(
        self,
        template_name: str,
        data: dict[str, Any],
        output_path: str | Path | None = None,
        width: int = 1080,
        height: int = 1350,
    ) -> str:
        """Render a template to PNG.

        Args:
            template_name: Name of the HTML template file (e.g., 'player_card.html')
            data: Dictionary of variables to pass to the template
            output_path: Where to save the PNG. If None, auto-generates.
            width: Canvas width in pixels
            height: Canvas height in pixels

        Returns:
            Path to the generated PNG file
        """
        template = self.env.get_template(template_name)

        # Inject CSS into data
        context = {
            **data,
            "css": self.css_cache,
            "width": width,
            "height": height,
        }

        html = template.render(context)

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html)
            temp_path = f.name

        try:
            # Use Playwright to render
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(f"file://{temp_path}")
                page.wait_for_load_state("networkidle")

                if output_path is None:
                    output_path = OUTPUT_DIR / f"{template_name.replace('.html', '')}.png"
                else:
                    output_path = Path(output_path)

                output_path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()

            return str(output_path)

        finally:
            os.unlink(temp_path)

    def query_player_card(self, player_name: str, season_year: int, competition_id: int) -> dict:
        """Fetch player data for the card template."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
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
                s.year,
                c.name AS competition
            FROM player_season_stats pss
            JOIN players p ON p.id = pss.player_id
            JOIN teams t ON t.id = pss.team_id
            JOIN seasons s ON s.id = pss.season_id
            JOIN competitions c ON c.id = s.competition_id
            WHERE p.full_name = %s AND s.year = %s AND s.competition_id = %s
            ORDER BY pss.minutes_played DESC
            LIMIT 1
            """,
            (player_name, season_year, competition_id),
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise ValueError(f"No data found for {player_name} in {season_year} competition {competition_id}")

        keys = [
            "player", "team", "goals", "assists", "rating",
            "minutes", "matches", "xg", "shots", "shots_on_target",
            "key_passes", "tackles", "interceptions", "pass_accuracy",
            "year", "competition",
        ]
        return dict(zip(keys, row))

    def generate_player_card(
        self,
        player_name: str,
        season_year: int = 2026,
        competition_id: int = 1,
        output_path: str | Path | None = None,
    ) -> str:
        """Generate a player card infographic."""
        data = self.query_player_card(player_name, season_year, competition_id)

        if output_path is None:
            safe_name = player_name.replace(" ", "_").lower()
            output_path = OUTPUT_DIR / f"player_card_{safe_name}_{season_year}_c{competition_id}.png"

        return self.render("player_card.html", data, output_path)


if __name__ == "__main__":
    # Test
    renderer = HTMLRenderer()
    path = renderer.generate_player_card("Maximiliano Guerrero", season_year=2026, competition_id=6)
    print(f"Generated: {path}")
