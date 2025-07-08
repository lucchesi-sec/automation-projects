"""
Logging Configuration

Centralized logging setup for the Smart File Organizer application.
Provides consistent logging across all modules.

AI Collaboration:
- Comprehensive logging for AI analysis and monitoring
- Structured log format for machine learning insights
- Performance metrics collection for optimization
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logger(name: str, 
                 level: str = "INFO",
                 log_file: Optional[str] = None,
                 console: bool = True) -> logging.Logger:
    """
    Set up a logger with consistent formatting and handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to log to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger