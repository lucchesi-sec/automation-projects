"""
Utility Module for Smart File Organizer

Contains helper functions, logging setup, and common utilities
used throughout the application.

AI Collaboration:
- Centralized logging for AI monitoring and analysis
- Helper functions for AI-enhanced operations
- Utility functions for data processing and formatting
"""

from .logger import setup_logger
from .helpers import format_file_size, get_file_hash, safe_filename

__all__ = [
    "setup_logger",
    "format_file_size",
    "get_file_hash",
    "safe_filename"
]