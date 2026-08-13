from loguru import logger

logger.add("logs/debug.log", rotation="10 MB", compression="zip")

ags_logger = logger
