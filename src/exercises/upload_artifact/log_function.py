#!/usr/bin/env python
import sys

from loguru import logger

from exercises.constants import LOGS_DIR


# ─────────────────────────────────────────────
# LOGGER SETUP
# ─────────────────────────────────────────────
def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
    )
    logger.add(
        LOGS_DIR / "pipeline.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
