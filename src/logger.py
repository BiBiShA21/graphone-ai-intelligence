from loguru import logger
import sys
from src.config import config

# Remove default handler
logger.remove()

# Add to file
logger.add(
    f"{config.LOGS_DIR}/pipeline.log",
    level=config.LOG_LEVEL,
    format="{time} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="500 MB"
)

# Add to console
logger.add(
    sys.stdout,
    level=config.LOG_LEVEL,
    format="{time} | {level: <8} | {message}"
)