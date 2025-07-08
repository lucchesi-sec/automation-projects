"""
Unit tests for the FileClassifier module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.file_organizer.core.classifier import FileClassifier


class TestFileClassifier:
    """Test cases for FileClassifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'classification': {
                'extensions': {
                    'documents': ['pdf', 'doc', 'txt'],
                    'images': ['jpg', 'png', 'gif'],
                    'videos': ['mp4', 'avi', 'mkv'],
                    'audio': ['mp3', 'wav', 'flac'],
                    'archives': ['zip', 'rar', '7z'],
                    'code': ['py', 'js', 'html']
                },
                'patterns': {
                    'screenshots': ['screenshot', 'screen_shot'],
                    'downloads': ['download', 'temp']
                }
            }
        }
        self.classifier = FileClassifier(self.config)
    
    def test_classify_by_extension_document(self):
        """Test classification of document files."""
        result = self.classifier.classify_file('document.pdf')
        assert result['category'] == 'documents'
        assert result['confidence'] > 0.7
    
    def test_classify_by_extension_image(self):
        """Test classification of image files."""
        result = self.classifier.classify_file('photo.jpg')
        assert result['category'] == 'images'
        assert result['confidence'] > 0.7
    
    def test_classify_by_extension_video(self):
        """Test classification of video files."""
        result = self.classifier.classify_file('video.mp4')
        assert result['category'] == 'videos'
        assert result['confidence'] > 0.7
    
    def test_classify_by_extension_audio(self):
        """Test classification of audio files."""
        result = self.classifier.classify_file('song.mp3')
        assert result['category'] == 'audio'
        assert result['confidence'] > 0.7
    
    def test_classify_by_extension_archive(self):
        """Test classification of archive files."""
        result = self.classifier.classify_file('archive.zip')
        assert result['category'] == 'archives'
        assert result['confidence'] > 0.7
    
    def test_classify_by_extension_code(self):
        """Test classification of code files."""
        result = self.classifier.classify_file('script.py')
        assert result['category'] == 'code'
        assert result['confidence'] > 0.7
    
    def test_classify_by_pattern_screenshot(self):
        """Test classification by filename pattern."""
        result = self.classifier.classify_file('screenshot_2023.png')
        assert result['subcategory'] == 'screenshots'
        assert result['confidence'] > 0.5
    
    def test_classify_unknown_extension(self):
        """Test classification of unknown file types."""
        result = self.classifier.classify_file('unknown.xyz')
        assert result['category'] == 'other'
        assert result['confidence'] < 0.5
    
    def test_classify_no_extension(self):
        """Test classification of files without extension."""
        result = self.classifier.classify_file('README')
        assert result['category'] == 'other'
        assert result['confidence'] < 0.5
    
    def test_case_insensitive_extension(self):
        """Test case insensitive extension matching."""
        result = self.classifier.classify_file('document.PDF')
        assert result['category'] == 'documents'
        assert result['confidence'] > 0.7
    
    def test_update_rules(self):
        """Test updating classification rules."""
        new_rules = {
            'extensions': {
                'documents': ['pdf', 'doc', 'txt', 'md'],
                'images': ['jpg', 'png', 'gif', 'svg']
            }
        }
        self.classifier.update_rules(new_rules)
        
        result = self.classifier.classify_file('readme.md')
        assert result['category'] == 'documents'