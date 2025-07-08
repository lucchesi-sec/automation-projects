"""
Configuration Validator

Validates YAML configuration files for correctness,
completeness, and proper structure.

AI Collaboration:
- Comprehensive validation for AI-driven configuration
- Detailed error reporting for debugging
- Extensible validation rules for new features
"""

from typing import Dict, Any, List, Optional
import logging

from ..utils.logger import setup_logger


class ConfigValidator:
    """
    Validates configuration files for correctness and completeness.
    
    Ensures configuration meets required structure and contains
    valid values for all settings.
    """
    
    def __init__(self):
        """Initialize the ConfigValidator."""
        self.logger = setup_logger(__name__)
        self.errors = []
        self.warnings = []
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate the complete configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Required top-level sections
        required_sections = ['classification', 'organization', 'logging']
        
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section: {section}")
            else:
                self._validate_section(section, config[section])
        
        # Report results
        if self.errors:
            self.logger.error(f"Configuration validation failed: {len(self.errors)} errors")
            for error in self.errors:
                self.logger.error(f"  - {error}")
        
        if self.warnings:
            self.logger.warning(f"Configuration warnings: {len(self.warnings)} warnings")
            for warning in self.warnings:
                self.logger.warning(f"  - {warning}")
        
        return len(self.errors) == 0    
    def _validate_section(self, section_name: str, section_config: Dict[str, Any]) -> None:
        """
        Validate a specific configuration section.
        
        Args:
            section_name: Name of the section
            section_config: Configuration for the section
        """
        if section_name == 'classification':
            self._validate_classification(section_config)
        elif section_name == 'organization':
            self._validate_organization(section_config)
        elif section_name == 'logging':
            self._validate_logging(section_config)
    
    def _validate_classification(self, config: Dict[str, Any]) -> None:
        """
        Validate classification configuration.
        
        Args:
            config: Classification configuration
        """
        if 'extensions' not in config:
            self.errors.append("Missing 'extensions' in classification section")
        else:
            extensions = config['extensions']
            if not isinstance(extensions, dict):
                self.errors.append("'extensions' must be a dictionary")
            else:
                for category, ext_list in extensions.items():
                    if not isinstance(ext_list, list):
                        self.errors.append(f"Extensions for '{category}' must be a list")
                    else:
                        for ext in ext_list:
                            if not isinstance(ext, str):
                                self.errors.append(f"Extension '{ext}' in category '{category}' must be a string")
        
        if 'patterns' in config:
            patterns = config['patterns']
            if not isinstance(patterns, dict):
                self.errors.append("'patterns' must be a dictionary")
            else:
                for category, pattern_list in patterns.items():
                    if not isinstance(pattern_list, list):
                        self.errors.append(f"Patterns for '{category}' must be a list")
    
    def _validate_organization(self, config: Dict[str, Any]) -> None:
        """
        Validate organization configuration.
        
        Args:
            config: Organization configuration
        """
        # Boolean settings
        bool_settings = ['create_date_folders', 'preserve_structure']
        for setting in bool_settings:
            if setting in config and not isinstance(config[setting], bool):
                self.errors.append(f"Setting '{setting}' must be a boolean")
        
        # Duplicate handling validation
        if 'duplicate_handling' in config:
            valid_options = ['rename', 'skip', 'overwrite']
            if config['duplicate_handling'] not in valid_options:
                self.errors.append(f"duplicate_handling must be one of: {valid_options}")
    
    def _validate_logging(self, config: Dict[str, Any]) -> None:
        """
        Validate logging configuration.
        
        Args:
            config: Logging configuration
        """
        if 'level' in config:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if config['level'] not in valid_levels:
                self.errors.append(f"Logging level must be one of: {valid_levels}")
        
        if 'file' in config and not isinstance(config['file'], str):
            self.errors.append("Logging file must be a string")