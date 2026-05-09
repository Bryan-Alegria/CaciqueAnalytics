"""Tests for Notifier."""

import logging

import pytest

from src.automation.notifier import Notifier


class TestNotifier:
    """Tests for the notification system."""

    def test_console_backend_logs_message(self, caplog):
        """Console backend should log the message."""
        notifier = Notifier(backend="console")
        with caplog.at_level(logging.INFO):
            notifier.send("Test message", level="info")
        assert "Test message" in caplog.text
        assert "[NOTIFIER]" in caplog.text

    def test_matchday_complete_message(self, caplog):
        """Should format matchday completion message."""
        notifier = Notifier(backend="console")
        with caplog.at_level(logging.INFO):
            notifier.matchday_complete(5, "Primera Division", 2026)
        assert "Matchday 5" in caplog.text
        assert "Primera Division" in caplog.text
        assert "Datos listos" in caplog.text

    def test_etl_complete_message(self, caplog):
        """Should format ETL completion message."""
        notifier = Notifier(backend="console")
        with caplog.at_level(logging.INFO):
            notifier.etl_complete({"inserted": 10, "updated": 5, "skipped": 0})
        assert "Insertados: 10" in caplog.text
        assert "Actualizados: 5" in caplog.text

    def test_error_message(self, caplog):
        """Should format error message."""
        notifier = Notifier(backend="console")
        with caplog.at_level(logging.ERROR):
            notifier.error("Connection failed")
        assert "Connection failed" in caplog.text
        assert "Error en pipeline" in caplog.text

    def test_invalid_backend_falls_back_to_console(self, caplog):
        """Unknown backend should fall back to console."""
        notifier = Notifier(backend="nonexistent")
        with caplog.at_level(logging.INFO):
            notifier.send("Fallback test", level="info")
        assert "Fallback test" in caplog.text

    def test_discord_without_webhook_falls_back(self, caplog):
        """Discord without webhook should fall back to console."""
        notifier = Notifier(backend="discord")
        with caplog.at_level(logging.WARNING):
            notifier.send("No webhook", level="info")
        assert "Discord webhook not configured" in caplog.text
        assert "falling back to console" in caplog.text
