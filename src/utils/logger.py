import os
from loguru import logger
import sys
from datetime import datetime

# Define a log format that is readable and user-friendly
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Add a console handler for terminal logging
logger.remove()  # Remove the default handler
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=os.getenv("LOG_LEVEL", "INFO").upper(),  # Change to DEBUG for verbose output
    colorize=True,
    backtrace=True,  # Show error backtraces for easier debugging
    diagnose=True,   # Show variable values in tracebacks
)

# Add a file handler for logging to a file with daily rotation
logger.add(
    f"logs/log_{datetime.now().strftime('%Y%m%d')}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="00:00",  # Rotate log files at midnight each day
    retention="7 days",  # Keep logs for 7 days
    compression="zip",  # Compress old logs
    level="DEBUG",  # Capture all levels in the log file
)

# Expose the logger for use in other files
__all__ = ["logger"]