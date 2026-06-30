import logging
import sys
from app.core.config import settings

def setup_logger() -> logging.Logger:
    """
    Configures structured logging for the application.
    Returns a centralized logger instance.
    """
    logger = logging.getLogger("rag_engine")
    
    # Prevent duplicate handlers if function is called multiple times
    if logger.handlers:
        return logger

    # Set log level based on configuration
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Create console handler with stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create a professional formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    # Prevent log messages from propagating to the root logger
    logger.propagate = False
    
    return logger

logger = setup_logger()
