"""
Unit tests for the configuration management modules.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from src.file_organizer.config.manager import ConfigManager
from src.file_organizer.config.validator import ConfigValidator


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / 'test_config.yaml'
    
    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        manager = ConfigManager(str(self.config_path))
        assert manager.config is not None
        assert 'classification' in manager.config
        assert 'organization' in manager.config
        assert 'logging' in manager.config
    
    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf', 'doc']
                }
            },
            'organization': {
                'create_date_folders': True
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
        
        # Save custom config
        with open(self.config_path, 'w') as f:
            yaml.dump(custom_config, f)
        
        manager = ConfigManager(str(self.config_path))
        assert manager.config['organization']['create_date_folders'] == True
        assert manager.config['logging']['level'] == 'DEBUG'
    
    def test_get_classification_rules(self):
        """Test getting classification rules."""
        manager = ConfigManager(str(self.config_path))
        rules = manager.get_classification_rules()
        
        assert 'extensions' in rules
        assert 'documents' in rules['extensions']
        assert 'pdf' in rules['extensions']['documents']
    
    def test_get_organization_settings(self):
        """Test getting organization settings."""
        manager = ConfigManager(str(self.config_path))
        settings = manager.get_organization_settings()
        
        assert 'create_date_folders' in settings
        assert 'duplicate_handling' in settings
        assert 'preserve_structure' in settings
    
    def test_reload_config(self):
        """Test reloading configuration."""
        manager = ConfigManager(str(self.config_path))
        
        # Modify config file
        new_config = manager.config.copy()
        new_config['organization']['create_date_folders'] = True
        
        with open(self.config_path, 'w') as f:
            yaml.dump(new_config, f)
        
        # Reload
        manager.reload_config()
        assert manager.config['organization']['create_date_folders'] == True


class TestConfigValidator:
    """Test cases for ConfigValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        valid_config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf', 'doc']
                },
                'patterns': {
                    'screenshots': ['screenshot']
                }
            },
            'organization': {
                'create_date_folders': False,
                'duplicate_handling': 'rename',
                'preserve_structure': False
            },
            'logging': {
                'level': 'INFO',
                'file': 'test.log'
            }
        }
        
        assert self.validator.validate(valid_config) == True
    
    def test_validate_missing_required_section(self):
        """Test validation with missing required section."""
        invalid_config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf']
                }
            }
            # Missing 'organization' and 'logging' sections
        }
        
        assert self.validator.validate(invalid_config) == False
    
    def test_validate_invalid_duplicate_handling(self):
        """Test validation with invalid duplicate handling option."""
        invalid_config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf']
                }
            },
            'organization': {
                'duplicate_handling': 'invalid_option'  # Invalid option
            },
            'logging': {
                'level': 'INFO'
            }
        }
        
        assert self.validator.validate(invalid_config) == False
    
    def test_validate_invalid_log_level(self):
        """Test validation with invalid log level."""
        invalid_config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf']
                }
            },
            'organization': {
                'duplicate_handling': 'rename'
            },
            'logging': {
                'level': 'INVALID_LEVEL'  # Invalid log level
            }
        }
        
        assert self.validator.validate(invalid_config) == False
    
    def test_get_errors(self):
        """Test getting validation errors."""
        invalid_config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf']
                }
            }
            # Missing required sections
        }
        
        self.validator.validate(invalid_config)
        errors = self.validator.get_errors()
        
        assert len(errors) > 0
        assert any('organization' in error for error in errors)
        assert any('logging' in error for error in errors)