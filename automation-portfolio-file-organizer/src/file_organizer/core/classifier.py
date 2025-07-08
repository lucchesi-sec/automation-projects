"""
File Classification System

Intelligent file classification using multiple strategies:
- File extension analysis
- Content analysis
- Pattern matching
- Machine learning potential (future enhancement)

AI Collaboration:
- Designed for easy integration with AI classification models
- Extensible architecture for new classification strategies
- Comprehensive logging for AI model training data
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from ..config.manager import ConfigManager
from ..utils.logger import setup_logger


class FileClassifier:
    """
    Intelligent file classification system with multiple strategies.
    
    Provides file categorization using extension analysis, content detection,
    and configurable rules with potential for AI enhancement.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the FileClassifier with configuration and detection systems.
        
        Sets up the multi-strategy classification system with:
        - Configuration-driven classification rules
        - MIME type detection system
        - Pattern matching capabilities
        - Extensible architecture for AI enhancement
        
        Args:
            config_manager: Configuration manager instance containing classification
                           rules, file type mappings, and pattern definitions
        
        Raises:
            AttributeError: If config_manager is invalid or missing required methods
            RuntimeError: If MIME type system initialization fails
        """
        # Initialize logging for classification operation tracking
        self.logger = setup_logger(__name__)
        
        # Store reference to configuration manager for rule access
        self.config_manager = config_manager
        
        # Load classification rules from configuration
        # These rules define file extension mappings and pattern matching
        self.rules = config_manager.get_classification_rules()
        
        # Initialize system MIME type detection
        # This enables content-based classification beyond just file extensions
        mimetypes.init()
        
        self.logger.info("FileClassifier initialized successfully")
    
    def classify_file(self, file_path: Path) -> Dict:
        """
        Classify a file using multiple detection strategies with confidence scoring.
        
        Employs a multi-strategy approach to determine file category:
        1. Extension analysis - Fast lookup based on file extension
        2. Content analysis - MIME type detection for accurate classification
        3. Pattern matching - Filename pattern recognition (e.g., "screenshot_")
        4. Confidence-based combination - Selects best result from all strategies
        
        Args:
            file_path: Path object or string path to the file requiring classification
            
        Returns:
            Dictionary containing classification results:
            - category: Primary category (e.g., 'documents', 'images', 'videos')
            - confidence: Confidence score from 0.0 to 1.0
            - method: Primary classification method used
            - primary_method: Most confident method (if combined)
            - details: List of results from all classification strategies
        
        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be accessed
            OSError: If filesystem error occurs during analysis
        """
        # Ensure we have a Path object for consistent handling
        file_path = Path(file_path)
        
        # Phase 1: Information Gathering
        # Collect comprehensive file metadata for all classification strategies
        file_info = self._gather_file_info(file_path)
        
        # Phase 2: Multi-Strategy Classification
        # Apply all classification strategies in parallel
        
        # Strategy 1: Extension-based classification (fast, reliable for known types)
        extension_result = self._classify_by_extension(file_info)
        
        # Strategy 2: Content-based classification (accurate, handles edge cases)
        content_result = self._classify_by_content(file_info)
        
        # Strategy 3: Pattern-based classification (handles special cases)
        pattern_result = self._classify_by_patterns(file_info)
        
        # Phase 3: Confidence-Based Result Combination
        # Select best classification result based on confidence scores
        final_classification = self._combine_classifications(
            extension_result, content_result, pattern_result
        )
        
        # Log classification result for monitoring and debugging
        self.logger.debug(f"Classified {file_path.name} as {final_classification}")
        
        return final_classification    
    def _gather_file_info(self, file_path: Path) -> Dict:
        """
        Gather comprehensive file metadata for all classification strategies.
        
        Collects essential file information including filesystem metadata,
        MIME type detection, and filename analysis. Handles errors gracefully
        to ensure classification can proceed even with limited information.
        
        Args:
            file_path: Path object pointing to the file for analysis
            
        Returns:
            Dictionary containing file metadata:
            - path: Original Path object
            - name: Complete filename with extension
            - stem: Filename without extension
            - suffix: File extension including dot (e.g., '.pdf')
            - size: File size in bytes (if accessible)
            - mime_type: MIME type string (if detectable)
            - is_hidden: Boolean indicating if file is hidden (starts with '.')
            - extension: File extension without dot (e.g., 'pdf')
        
        Note:
            Falls back to basic information if filesystem operations fail,
            ensuring classification can proceed with available data.
        """
        try:
            # Attempt to gather complete filesystem metadata
            stat = file_path.stat()
            
            # Use system MIME type detection for content analysis
            # Returns tuple (mime_type, encoding), we only need mime_type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Compile comprehensive file information dictionary
            return {
                'path': file_path,                              # Original Path object
                'name': file_path.name,                         # Complete filename
                'stem': file_path.stem,                         # Filename without extension
                'suffix': file_path.suffix.lower(),             # Extension with dot (normalized)
                'size': stat.st_size,                           # File size in bytes
                'mime_type': mime_type,                         # MIME type for content analysis
                'is_hidden': file_path.name.startswith('.'),    # Hidden file detection
                'extension': file_path.suffix.lower().lstrip('.') # Extension without dot
            }
            
        except Exception as e:
            # Log error but continue with basic information
            # This ensures classification can proceed even with filesystem issues
            self.logger.error(f"Error gathering file info for {file_path}: {e}")
            
            # Return minimal information that can be extracted without filesystem access
            return {
                'path': file_path,
                'name': file_path.name,
                'stem': file_path.stem,
                'suffix': file_path.suffix.lower(),
                'extension': file_path.suffix.lower().lstrip('.')
            }
    
    def _classify_by_extension(self, file_info: Dict) -> Dict:
        """
        Classify file based on extension using configuration-driven rules.
        
        Performs fast extension-based classification using configured mappings.
        This is the most reliable method for known file types and provides
        high confidence results when matches are found.
        
        Args:
            file_info: File information dictionary containing 'extension' key
            
        Returns:
            Classification result dictionary:
            - category: File category (e.g., 'documents', 'images', 'videos')
            - confidence: Confidence score (0.8 for matches, 0.3 for unknown)
            - method: Always 'extension' for this strategy
        
        Note:
            Confidence of 0.8 reflects high reliability of extension-based
            classification for known file types. Unknown extensions receive
            lower confidence of 0.3 to allow other strategies to take priority.
        """
        # Extract normalized extension (without dot)
        extension = file_info['extension']
        
        # Search through configured extension mappings
        # Configuration format: {'documents': ['pdf', 'doc'], 'images': ['jpg', 'png']}
        for category, extensions in self.rules.get('extensions', {}).items():
            if extension in extensions:
                # High confidence for known extension mappings
                # 0.8 confidence reflects strong reliability of extension-based classification
                return {
                    'category': category,
                    'confidence': 0.8,  # High confidence for known extensions
                    'method': 'extension'
                }
        
        # Handle unknown extensions with lower confidence
        # This allows other classification strategies to potentially override
        return {
            'category': 'uncategorized',
            'confidence': 0.3,  # Lower confidence for unknown extensions
            'method': 'extension'
        }    
    def _classify_by_content(self, file_info: Dict) -> Dict:
        """
        Classify file using MIME type content analysis for accurate categorization.
        
        Uses system MIME type detection to classify files based on their actual
        content rather than just filename extensions. This is more accurate than
        extension-based classification and can handle files with incorrect or
        missing extensions.
        
        Args:
            file_info: File information dictionary containing 'mime_type' key
            
        Returns:
            Classification result dictionary:
            - category: File category based on MIME type
            - confidence: Confidence score (0.9 for matches, 0.1-0.2 for failures)
            - method: Always 'content' for this strategy
        
        Note:
            Confidence of 0.9 reflects high accuracy of MIME type detection.
            This is the highest confidence among all classification strategies
            because MIME types are based on actual file content analysis.
        """
        # Extract MIME type from file information
        mime_type = file_info.get('mime_type', '')
        
        # Handle cases where MIME type detection failed
        if not mime_type:
            return {'category': 'uncategorized', 'confidence': 0.1, 'method': 'content'}
        
        # MIME type to category mapping
        # Uses prefix matching to handle MIME type variations
        # e.g., 'image/' matches 'image/jpeg', 'image/png', etc.
        mime_mappings = {
            'image/': 'images',                                      # All image types
            'video/': 'videos',                                      # All video types
            'audio/': 'audio',                                       # All audio types
            'text/': 'documents',                                    # Text documents
            'application/pdf': 'documents',                          # PDF documents
            'application/msword': 'documents',                       # Word documents
            'application/vnd.openxmlformats-officedocument': 'documents',  # Office documents
            'application/zip': 'archives',                           # ZIP archives
            'application/x-rar': 'archives',                         # RAR archives
            'application/x-7z': 'archives'                           # 7-Zip archives
        }
        
        # Search for MIME type matches using prefix matching
        for mime_pattern, category in mime_mappings.items():
            if mime_type.startswith(mime_pattern):
                # Highest confidence for MIME type matches
                # 0.9 confidence reflects high accuracy of content-based classification
                return {
                    'category': category,
                    'confidence': 0.9,  # Highest confidence for content analysis
                    'method': 'content'
                }
        
        # Handle unrecognized MIME types with low confidence
        return {'category': 'uncategorized', 'confidence': 0.2, 'method': 'content'}
    
    def _classify_by_patterns(self, file_info: Dict) -> Dict:
        """
        Classify file using filename pattern matching for special cases.
        
        Handles specialized file categorization based on filename patterns
        that indicate specific file purposes or origins. This is useful for
        files like screenshots, downloads, or backups that may not be
        accurately classified by extension or MIME type alone.
        
        Args:
            file_info: File information dictionary containing 'name' key
            
        Returns:
            Classification result dictionary:
            - category: File category based on pattern match
            - confidence: Confidence score (0.7 for matches, 0.1 for no match)
            - method: Always 'pattern' for this strategy
        
        Examples:
            - "screenshot_2023.png" -> category: 'screenshots'
            - "download_temp.pdf" -> category: 'downloads'
            - "backup_old.zip" -> category: 'backups'
        
        Note:
            Confidence of 0.7 balances reliability with the possibility of
            false positives from pattern matching. Lower than content analysis
            but higher than unknown extension classification.
        """
        # Convert filename to lowercase for case-insensitive pattern matching
        name = file_info['name'].lower()
        
        # Load pattern rules from configuration
        # Configuration format: {'screenshots': ['screenshot', 'screen_shot'], 'downloads': ['download', 'temp']}
        patterns = self.rules.get('patterns', {})
        
        # Search through all configured patterns
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                # Check if pattern exists anywhere in the filename
                if pattern in name:
                    # Medium confidence for pattern matches
                    # 0.7 confidence balances usefulness with false positive risk
                    return {
                        'category': category,
                        'confidence': 0.7,  # Medium confidence for pattern matching
                        'method': 'pattern'
                    }
        
        # No pattern matches found
        return {'category': 'uncategorized', 'confidence': 0.1, 'method': 'pattern'}    
    def _combine_classifications(self, *results: Dict) -> Dict:
        """
        Combine multiple classification results using confidence-based selection.
        
        Implements a sophisticated strategy selection algorithm that chooses the
        most confident classification result while filtering out low-confidence
        uncategorized results. This ensures the best available classification
        is selected from all strategies.
        
        Args:
            *results: Variable number of classification result dictionaries from
                     different strategies (extension, content, pattern)
            
        Returns:
            Combined classification result dictionary:
            - category: Best category from highest confidence result
            - confidence: Highest confidence score among valid results
            - method: Always 'combined' for this final result
            - primary_method: Method that provided the winning result
            - details: List of all individual classification results
        
        Algorithm:
            1. Filter out low-confidence uncategorized results (< 0.5)
            2. If no valid results remain, return uncategorized
            3. Select result with highest confidence score
            4. Return combined result with full details
        
        Note:
            The 0.5 confidence threshold filters out weak uncategorized results
            while preserving strong classifications from any strategy.
        """
        # Phase 1: Filter Classification Results
        # Remove uncategorized results with low confidence to prioritize actual classifications
        # Threshold of 0.5 ensures only confident uncategorized results are preserved
        valid_results = [r for r in results if r['category'] != 'uncategorized' or r['confidence'] > 0.5]
        
        # Phase 2: Handle No Valid Classifications
        # If all strategies failed or returned low-confidence results
        if not valid_results:
            return {
                'category': 'uncategorized',
                'confidence': 0.1,           # Low confidence for fallback
                'method': 'combined',
                'details': list(results)     # Preserve all attempts for debugging
            }
        
        # Phase 3: Select Best Classification
        # Choose the result with highest confidence score
        # This naturally prioritizes: content (0.9) > extension (0.8) > pattern (0.7)
        best_result = max(valid_results, key=lambda x: x['confidence'])
        
        # Phase 4: Compile Final Result
        # Combine best classification with full provenance information
        return {
            'category': best_result['category'],        # Winning category
            'confidence': best_result['confidence'],    # Winning confidence score
            'method': 'combined',                       # Indicates multi-strategy result
            'primary_method': best_result['method'],    # Strategy that won
            'details': list(results)                    # All strategy results for analysis
        }