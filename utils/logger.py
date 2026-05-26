"""
utils/logger.py
Centralized logging for A.H.I. — logs to both Rich console and rotating file.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

console = Console()

_logger_initialized = False
_logger = None


def get_logger(name: str = "AHI", config: dict = None) -> logging.Logger:
    global _logger_initialized, _logger

    if _logger_initialized and _logger:
        return logging.getLogger(name)

    # Defaults
    log_level = logging.INFO
    log_file = "data/logs/jane.log"
    max_bytes = 5 * 1024 * 1024  # 5 MB
    backup_count = 3

    if config:
        log_cfg = config.get("logging", {})
        level_str = log_cfg.get("level", "INFO").upper()
        log_level = getattr(logging, level_str, logging.INFO)
        log_file = log_cfg.get("file", log_file)
        max_bytes = log_cfg.get("max_bytes", max_bytes)
        backup_count = log_cfg.get("backup_count", backup_count)

    # Ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    if not logger.handlers:
        # Rich console handler (pretty)
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
        )
        rich_handler.setLevel(logging.WARNING)
        logger.addHandler(rich_handler)

        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    _logger = logger
    _logger_initialized = True
    return logger
