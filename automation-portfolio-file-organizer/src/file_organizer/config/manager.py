"""
Configuration Manager

Handles loading, validation, and management of YAML-based
configuration files for file organization rules.

AI Collaboration:
- Extensible configuration system for AI integration
- Dynamic rule loading and validation
- Comprehensive error handling and logging
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .validator import ConfigValidator
from ..utils.logger import setup_logger


class ConfigManager:
    """
    Manages YAML-based configuration for file organization.
    
    Provides centralized configuration management with validation,
    defaults, and dynamic reloading capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.logger = setup_logger(__name__)
        self.config_path = self._resolve_config_path(config_path)
        self.validator = ConfigValidator()
        self.config = self._load_config()
        
        self.logger.info(f"ConfigManager initialized with: {self.config_path}")
    
    def _resolve_config_path(self, config_path: Optional[str]) -> Path:
        """
        Resolve the configuration file path.
        
        Args:
            config_path: User-provided path or None
            
        Returns:
            Resolved Path object
        """
        if config_path:
            return Path(config_path)
            
        # Default locations to check
        default_locations = [
            Path.cwd() / "config.yaml",
            Path.cwd() / "file_organizer.yaml",
            Path.home() / ".file_organizer" / "config.yaml",
            Path(__file__).parent / "default_config.yaml"
        ]
        
        for location in default_locations:
            if location.exists():
                return location
                
        # Return default config path for creation
        return Path.cwd() / "config.yaml"    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    
                if self.validator.validate(config):
                    self.logger.info("Configuration loaded successfully")
                    return config
                else:
                    self.logger.error("Configuration validation failed")
                    return self._get_default_config()
                    
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return self._get_default_config()
        else:
            self.logger.info("Creating default configuration")
            config = self._get_default_config()
            self._save_config(config)
            return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'classification': {
                'extensions': {
                    'documents': [
                        'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
                        'xls', 'xlsx', 'ppt', 'pptx', 'csv'
                    ],
                    'images': [
                        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
                        'svg', 'webp', 'ico', 'raw'
                    ],
                    'videos': [
                        'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv',
                        'webm', 'm4v', '3gp', 'mpg', 'mpeg'
                    ],
                    'audio': [
                        'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma',
                        'm4a', 'opus', 'aiff'
                    ],
                    'archives': [
                        'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
                        'xz', 'dmg', 'iso'
                    ],
                    'code': [
                        'py', 'js', 'html', 'css', 'java', 'cpp',
                        'c', 'h', 'php', 'rb', 'go', 'rs', 'swift'
                    ]
                },
                'patterns': {
                    'screenshots': ['screenshot', 'screen_shot', 'capture'],
                    'downloads': ['download', 'temp', 'tmp'],
                    'backups': ['backup', 'bak', 'old', 'copy']
                }
            },
            'organization': {
                'create_date_folders': False,
                'duplicate_handling': 'rename',
                'preserve_structure': False
            },
            'logging': {
                'level': 'INFO',
                'file': 'file_organizer.log'
            }
        }    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def get_classification_rules(self) -> Dict[str, Any]:
        """
        Get classification rules from config.
        
        Returns:
            Classification rules dictionary
        """
        return self.config.get('classification', {})
    
    def get_organization_settings(self) -> Dict[str, Any]:
        """
        Get organization settings from config.
        
        Returns:
            Organization settings dictionary
        """
        return self.config.get('organization', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Logging configuration dictionary
        """
        return self.config.get('logging', {})
    
    def reload_config(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config = self._load_config()
            self.logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error reloading config: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config.update(updates)
            self._save_config(self.config)
            self.logger.info("Configuration updated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            return False