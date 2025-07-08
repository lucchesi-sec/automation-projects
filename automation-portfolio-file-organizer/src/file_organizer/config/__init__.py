"""
Configuration Management Module

Handles YAML-based configuration for file organization rules,
classification settings, and system behavior.

AI Collaboration:
- Flexible configuration system for AI-powered enhancements
- YAML-based rules for easy modification and learning
- Validation and error handling for robust operation
"""

from .manager import ConfigManager
from .validator import ConfigValidator

__all__ = [
    "ConfigManager",
    "ConfigValidator"
]