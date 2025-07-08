"""
Smart File Organizer - AI-Powered File Management System

This module provides intelligent file organization capabilities with
machine learning-based classification and customizable rules.

Author: Enzo Lucchesi
Created: 2025-07-08
AI Collaboration: Claude Code Assistant
"""

__version__ = "1.0.0"
__author__ = "Enzo Lucchesi"
__email__ = "your.email@example.com"

from .core.organizer import FileOrganizer
from .core.classifier import FileClassifier
from .config.manager import ConfigManager

__all__ = [
    "FileOrganizer",
    "FileClassifier", 
    "ConfigManager",
    "__version__",
    "__author__",
    "__email__"
]