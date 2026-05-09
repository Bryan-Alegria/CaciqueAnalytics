"""Notification system for automation events."""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class Notifier:
    """Send notifications when automation events occur.

    Supports multiple backends:
    - console (default): log messages
    - discord: webhook notifications
    - email: SMTP notifications (not implemented)
    - windows: Windows toast notifications (not implemented)
    """

    def __init__(
        self,
        backend: str = "console",
        discord_webhook: Optional[str] = None,
    ):
        self.backend = backend
        self.discord_webhook = discord_webhook or os.getenv("DISCORD_WEBHOOK_URL")

    def send(self, message: str, level: str = "info") -> None:
        """Send a notification.

        Args:
            message: The notification message
            level: Log level (info, warning, error, success)
        """
        if self.backend == "console":
            self._send_console(message, level)
        elif self.backend == "discord":
            self._send_discord(message, level)
        elif self.backend == "windows":
            self._send_windows(message, level)
        else:
            self._send_console(message, level)

    def _send_console(self, message: str, level: str) -> None:
        """Log to console via Python logging."""
        log_method = getattr(logger, level, logger.info)
        log_method(f"[NOTIFIER] {message}")

    def _send_discord(self, message: str, level: str) -> None:
        """Send a message to a Discord webhook."""
        if not self.discord_webhook:
            logger.warning("Discord webhook not configured, falling back to console")
            self._send_console(message, level)
            return

        try:
            import requests

            color_map = {
                "info": 3447003,
                "warning": 16776960,
                "error": 15158332,
                "success": 3066993,
            }

            payload = {
                "embeds": [
                    {
                        "description": message,
                        "color": color_map.get(level, 3447003),
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
                    }
                ]
            }

            resp = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            logger.info("Discord notification sent")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            self._send_console(message, level)

    def _send_windows(self, message: str, level: str) -> None:
        """Show a Windows toast notification."""
        try:
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast(
                "CaciqueAnalytics",
                message,
                duration=10,
                threaded=True,
            )
        except ImportError:
            logger.warning("win10toast not installed, falling back to console")
            self._send_console(message, level)
        except Exception as e:
            logger.error(f"Failed to show Windows notification: {e}")
            self._send_console(message, level)

    def matchday_complete(self, matchday: int, competition: str, season: int) -> None:
        """Notify that a matchday is complete and data is ready."""
        message = (
            f"Matchday {matchday} de {competition} {season} completado. "
            f"Datos listos para exportacion."
        )
        self.send(message, level="success")

    def etl_complete(self, stats: dict) -> None:
        """Notify that ETL completed."""
        inserted = stats.get("inserted", 0)
        updated = stats.get("updated", 0)
        skipped = stats.get("skipped", 0)
        message = (
            f"ETL completado. Insertados: {inserted}, Actualizados: {updated}, "
            f"Omitidos: {skipped}"
        )
        self.send(message, level="info")

    def error(self, error_message: str) -> None:
        """Notify about an error."""
        self.send(f"Error en pipeline: {error_message}", level="error")
