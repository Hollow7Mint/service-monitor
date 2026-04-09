import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)
_MAX_RETRIES = 3


class App:
    def __init__(self, debug: bool = False, dry_run: bool = False) -> None:
        self.debug   = debug
        self.dry_run = dry_run
        self._started    = False
        self._components: list[Any] = []
        self._hooks: dict[str, list] = {"startup": [], "shutdown": []}

    def on_startup(self, fn) -> None:
        self._hooks["startup"].append(fn)

    def on_shutdown(self, fn) -> None:
        self._hooks["shutdown"].append(fn)

    def _run_hooks(self, event: str) -> None:
        for fn in self._hooks.get(event, []):
            try:
                fn()
            except Exception as exc:
                logger.error("Hook %s raised: %s", fn.__name__, exc)

    def _load_components(self) -> None:
        logger.debug("Loading components")
        self._components = []

    def _warmup(self) -> bool:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                self._load_components()
                return True
            except Exception as exc:
                logger.warning("Warmup attempt %d/%d: %s", attempt, _MAX_RETRIES, exc)
                time.sleep(0.5 * attempt)
        return False

    def run(self) -> None:
        logger.info("Starting (debug=%s dry_run=%s)", self.debug, self.dry_run)
        if not self._warmup():
            logger.error("Warmup failed, aborting")
            return
        self._started = True
        self._run_hooks("startup")
        try:
            self._main_loop()
        finally:
            self.shutdown()

    def _main_loop(self) -> None:
        if self.dry_run:
            logger.info("[dry-run] skipping main loop")
            return
        logger.info("Running main loop")

    def shutdown(self) -> None:
        if not self._started:
            return
        self._run_hooks("shutdown")
        self._components.clear()
        self._started = False
        logger.info("Shutdown complete")

    def status(self) -> dict:
        return {
            "started":    self._started,
            "debug":      self.debug,
            "dry_run":    self.dry_run,
            "components": len(self._components),
        }
