# I got this from media forge bot. Check them out https://github.com/HexCodeFFF/mediaforge
"""Enhanced logging configuration for ChezziBot."""

import logging
import sys
from pathlib import Path
from typing import Optional

import coloredlogs
import config

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Set up a logger with colored output and file logging."""
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = getattr(logging, (level or config.LOG_LEVEL).upper())
    logger.setLevel(log_level)
    
    # Remove existing handlers to prevent duplication
    logger.handlers.clear()
    
    # Console handler with colors
    coloredlogs.install(
        level=log_level,
        logger=logger,
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
        field_styles={
            'levelname': {'bold': True, 'color': 'blue'},
            'asctime': {'color': 'green'},
            'name': {'color': 'cyan'},
            'funcName': {'color': 'yellow'},
            'lineno': {'color': 'magenta'}
        }
    )
    
    # File handler
    log_file = Path("logs") / f"{name}.log"
    log_file.parent.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
    )
    logger.addHandler(file_handler)
    
    return logger

# Main bot logger
logger = setup_logger("chezzibot")

# Discord.py logger
if config.ENABLE_DPY_LOGGING:
    discord_logger = setup_logger("discord", "DEBUG")
