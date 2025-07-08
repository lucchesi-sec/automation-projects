"""
Core module for Smart File Organizer

Contains the main organization engine, classification system,
and core file management functionality.

AI Collaboration Notes:
- Engine designed with modularity for easy AI-assisted enhancement
- Classification system built for extensibility
- Logging integrated for AI analysis and monitoring
"""

from .organizer import FileOrganizer
from .classifier import FileClassifier
from .scanner import FileScanner

__all__ = [
    "FileOrganizer",
    "FileClassifier",
    "FileScanner"
]