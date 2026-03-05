#!/usr/bin/env python
import sys
from pathlib import Path

from loguru import logger

# 1. Diretório raiz
ROOT_DIR = Path(__file__).resolve().parent

# 2. Define os subdiretórios
LOGS_DIR = ROOT_DIR / "logs"

# 3. Opcional: Garante que eles existam ao rodar o projeto
for directory in [LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


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


if __name__ == "__main__":
    print(ROOT_DIR)
