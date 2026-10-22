"""Application-wide logging configuration."""

import logging
import os
from pathlib import Path


DEFAULT_LOG_FILE = Path("logs") / "claims-agent.log"


def configure_logging() -> None:
    """Configure application logging to write to the configured file."""
    log_file = Path(os.getenv("CLAIMS_AGENT_LOG_FILE", str(DEFAULT_LOG_FILE))).expanduser()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    resolved_log_file = log_file.resolve()

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if getattr(handler, "_claims_agent_file_handler", False):
            if Path(handler.baseFilename) == resolved_log_file:
                return
            root_logger.removeHandler(handler)
            handler.close()

    file_handler = logging.FileHandler(resolved_log_file, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    file_handler._claims_agent_file_handler = True
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
