import argparse
import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level: str, log_file: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LOG_FORMAT,
        handlers=handlers,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Application entry point",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--log-file", default=None)
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging("DEBUG" if args.debug else "INFO", args.log_file)
    logger = logging.getLogger(__name__)

    if not Path(args.config).exists():
        logger.warning("Config not found at %s, using defaults", args.config)

    from app import App
    try:
        app = App(debug=args.debug, dry_run=args.dry_run)
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        return 130
    except Exception as exc:
        logger.exception("Fatal: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
