"""
utils/logger.py
Centralized logging — Rich console + rotating file.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

console = Console()
_initialized = False


def get_logger(name: str = "AHI", config: dict = None) -> logging.Logger:
    global _initialized

    logger = logging.getLogger(name)

    if _initialized:
        return logger

    # Defaults
    log_level = logging.INFO
    log_file = "data/logs/jane.log"
    max_bytes = 5 * 1024 * 1024
    backup_count = 3

    if config:
        log_cfg = config.get("logging", {})
        log_level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
        log_file = log_cfg.get("file", log_file)
        max_bytes = log_cfg.get("max_bytes", max_bytes)
        backup_count = log_cfg.get("backup_count", backup_count)

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(log_level)
    logger.propagate = False

    if not logger.handlers:
        # Rich handler — only WARNING+ to console to keep UI clean
        rich_handler = RichHandler(console=console, show_time=True, show_path=False, rich_tracebacks=True)
        rich_handler.setLevel(logging.WARNING)
        logger.addHandler(rich_handler)

        # File handler — full detail
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(file_handler)

    _initialized = True
    return logger
