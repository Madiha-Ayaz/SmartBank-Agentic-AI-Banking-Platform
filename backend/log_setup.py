from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger

from backend.config import settings


def setup_logging() -> None:
    level = logging.getLevelName(settings.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    uvicorn_logger.addHandler(handler)
    uvicorn_logger.setLevel(level)

    logging.getLogger("passlib").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
