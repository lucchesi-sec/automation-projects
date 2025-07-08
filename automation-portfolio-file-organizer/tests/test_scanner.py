"""
Unit tests for the FileScanner module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.file_organizer.core.scanner import FileScanner


class TestFileScanner:
    """Test cases for FileScanner."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'scanner': {
                'recursive': True,
                'max_depth': 5,
                'ignore_hidden': True,
                'ignore_system': True
            }
        }
        self.logger = Mock()
        self.scanner = FileScanner(self.config, self.logger)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_scan_directory_not_exists(self, mock_is_dir, mock_exists):
        """Test scanning non-existent directory."""
        mock_exists.return_value = False
        
        result = self.scanner.scan_directory('/nonexistent/path')
        assert result == []
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_scan_directory_not_directory(self, mock_is_dir, mock_exists):
        """Test scanning path that is not a directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = False
        
        result = self.scanner.scan_directory('/path/to/file.txt')
        assert result == []
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.iterdir')
    def test_scan_directory_with_files(self, mock_iterdir, mock_is_dir, mock_exists):
        """Test scanning directory with files."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        # Mock file objects
        mock_file1 = Mock()
        mock_file1.is_file.return_value = True
        mock_file1.name = 'document.pdf'
        mock_file1.stat.return_value.st_size = 1024
        
        mock_file2 = Mock()
        mock_file2.is_file.return_value = True
        mock_file2.name = 'image.jpg'
        mock_file2.stat.return_value.st_size = 2048
        
        mock_iterdir.return_value = [mock_file1, mock_file2]
        
        result = self.scanner.scan_directory('/test/path')
        assert len(result) == 2
    
    def test_should_ignore_hidden_file(self):
        """Test ignoring hidden files."""
        assert self.scanner._should_ignore_file('.hidden_file') == True
        assert self.scanner._should_ignore_file('normal_file.txt') == False
    
    def test_should_ignore_system_file(self):
        """Test ignoring system files."""
        assert self.scanner._should_ignore_file('Thumbs.db') == True
        assert self.scanner._should_ignore_file('.DS_Store') == True
        assert self.scanner._should_ignore_file('desktop.ini') == True
        assert self.scanner._should_ignore_file('normal_file.txt') == False
    
    def test_should_ignore_temporary_file(self):
        """Test ignoring temporary files."""
        assert self.scanner._should_ignore_file('~temp.tmp') == True
        assert self.scanner._should_ignore_file('file.tmp') == True
        assert self.scanner._should_ignore_file('normal_file.txt') == False
    
    def test_update_config(self):
        """Test updating scanner configuration."""
        new_config = {
            'scanner': {
                'recursive': False,
                'max_depth': 2,
                'ignore_hidden': False,
                'ignore_system': False
            }
        }
        
        self.scanner.update_config(new_config)
        
        assert self.scanner.recursive == False
        assert self.scanner.max_depth == 2
        assert self.scanner.ignore_hidden == False
        assert self.scanner.ignore_system == False
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.iterdir')
    def test_scan_directory_recursive_depth_limit(self, mock_iterdir, mock_is_dir, mock_exists):
        """Test recursive scanning with depth limit."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_iterdir.return_value = []
        
        # Set max depth to 1
        self.scanner.max_depth = 1
        
        # Should not scan beyond depth 1
        result = self.scanner.scan_directory('/test/path', depth=2)
        assert result == []