"""Scheduler for running automation cycles.

Can be run directly or invoked via Windows Task Scheduler."""

import argparse
import logging
import sys
from datetime import datetime, timezone

from src.automation.notifier import Notifier
from src.automation.trigger import AutomationTrigger

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the scheduler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_cycle(
    competition_ids: list[int] | None = None,
    season_ids: list[int] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run a single automation cycle.

    Args:
        competition_ids: Filter by competitions
        season_ids: Filter by seasons
        dry_run: If True, only report what would happen

    Returns:
        Results dict from the trigger
    """
    trigger = AutomationTrigger()

    if dry_run:
        return trigger.dry_run(season_ids)

    return trigger.run(competition_ids, season_ids)


def main() -> int:
    """CLI entry point for the scheduler."""
    parser = argparse.ArgumentParser(
        description="CaciqueAnalytics automation scheduler"
    )
    parser.add_argument(
        "--competition",
        type=int,
        action="append",
        help="Competition ID to process (can be used multiple times)",
    )
    parser.add_argument(
        "--season",
        type=int,
        action="append",
        help="Season ID to process (can be used multiple times)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without executing",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    logger.info("CaciqueAnalytics scheduler starting")
    logger.info(f"Mode: {'dry-run' if args.dry_run else 'live'}")

    try:
        results = run_cycle(
            competition_ids=args.competition,
            season_ids=args.season,
            dry_run=args.dry_run,
        )

        logger.info("Cycle results:")
        for key, value in results.items():
            if isinstance(value, list):
                logger.info(f"  {key}: {len(value)} items")
                for item in value[:5]:
                    logger.info(f"    - {item}")
            else:
                logger.info(f"  {key}: {value}")

        notifier = Notifier()
        notifier.send("Ciclo de automatizacion completado exitosamente", level="success")

        return 0

    except Exception as e:
        logger.exception("Automation cycle failed")
        notifier = Notifier()
        notifier.error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
