"""
Main File Organizer Engine

Core orchestration engine that coordinates file discovery, classification,
and organization operations.

AI Collaboration:
- Designed for extensibility with AI-powered classification
- Modular architecture allows for easy AI feature integration
- Comprehensive logging for AI analysis and optimization
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .classifier import FileClassifier
from .scanner import FileScanner
from ..config.manager import ConfigManager
from ..utils.logger import setup_logger


class FileOrganizer:
    """
    Main orchestration engine for intelligent file organization.
    
    Coordinates file discovery, classification, and organization
    operations with comprehensive logging and error handling.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the FileOrganizer with configuration and dependencies.
        
        Sets up the complete file organization pipeline including:
        - Configuration management system
        - File classification engine
        - Directory scanning capabilities
        - Statistics tracking for performance monitoring
        
        Args:
            config_path: Optional path to custom configuration file.
                        If None, uses default configuration locations.
        
        Raises:
            ConfigurationError: If configuration file is invalid
            ImportError: If required dependencies are missing
        """
        # Initialize logging system for comprehensive operation tracking
        self.logger = setup_logger(__name__)
        
        # Load and validate configuration - this drives all classification rules
        self.config_manager = ConfigManager(config_path)
        
        # Initialize file classification engine with loaded configuration
        self.classifier = FileClassifier(self.config_manager)
        
        # Initialize directory scanner for file discovery
        self.scanner = FileScanner()
        
        # Initialize statistics tracking for performance monitoring and AI analysis
        # These metrics are crucial for understanding organization effectiveness
        self.stats = {
            'files_processed': 0,      # Total files encountered during organization
            'files_moved': 0,          # Files successfully moved to target locations
            'errors': 0,               # Count of errors encountered during processing
            'start_time': None,        # Organization start timestamp
            'end_time': None           # Organization completion timestamp
        }
        
        self.logger.info("FileOrganizer initialized successfully")
    
    def organize_directory(self, source_path: str, 
                         target_path: str = None,
                         dry_run: bool = False) -> Dict:
        """
        Organize files in the specified directory using intelligent classification.
        
        This is the main entry point for file organization operations. It orchestrates
        the complete workflow: file discovery, classification, and organization into
        categorized directories.
        
        Args:
            source_path: Directory containing files to organize. Must exist and be readable.
            target_path: Target directory for organized files. If None, files are organized
                        in-place within the source directory. If specified, creates a new
                        organized directory structure.
            dry_run: If True, simulates the organization process without actually moving
                    files. Useful for previewing changes before execution.
            
        Returns:
            Dictionary containing:
            - 'files': List of individual file processing results
            - 'statistics': Performance metrics including:
                - files_processed: Total files encountered
                - files_moved: Files successfully relocated
                - errors: Count of processing errors
                - duration_seconds: Total processing time
                - success_rate: Percentage of successful operations
        
        Raises:
            FileNotFoundError: If source directory doesn't exist
            PermissionError: If insufficient permissions for file operations
            OSError: If filesystem operations fail
        """
        # Record operation start time for performance metrics
        self.stats['start_time'] = datetime.now()
        
        # Convert source path to Path object for robust filesystem operations
        source_path = Path(source_path)
        
        # Validate source directory exists before proceeding
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory does not exist: {source_path}")
            
        # Handle target path logic: None means in-place organization
        if target_path is None:
            target_path = source_path  # Organize files within source directory
        else:
            target_path = Path(target_path)  # Convert to Path object for consistency
            
        self.logger.info(f"Starting organization: {source_path} -> {target_path}")
        
        # Phase 1: File Discovery
        # Use scanner to recursively discover all files in source directory
        files = self.scanner.scan_directory(source_path)
        self.logger.info(f"Found {len(files)} files to process")
        
        # Phase 2: File Processing
        # Process each discovered file individually to maintain error isolation
        results = []
        for file_path in files:
            try:
                # Attempt to organize individual file
                result = self._organize_file(file_path, target_path, dry_run)
                results.append(result)
                
                # Track successful processing for statistics
                self.stats['files_processed'] += 1
                
            except Exception as e:
                # Log individual file errors without stopping batch processing
                # This ensures one problematic file doesn't halt entire operation
                self.logger.error(f"Error processing {file_path}: {e}")
                self.stats['errors'] += 1
                
        # Record completion time for performance analysis
        self.stats['end_time'] = datetime.now()
        
        # Phase 3: Results Compilation
        # Compile individual results into comprehensive summary with statistics
        return self._compile_results(results)
    
    def _organize_file(self, file_path: Path, target_base: Path, 
                      dry_run: bool) -> Dict:
        """
        Process a single file through the complete organization pipeline.
        
        This method handles the core logic for individual file organization:
        1. File classification using AI-powered analysis
        2. Target location determination based on classification
        3. Naming conflict resolution
        4. Actual file relocation (if not dry run)
        
        Args:
            file_path: Path object pointing to the file to organize
            target_base: Base directory where organized files will be placed
            dry_run: If True, simulates the move without actual file operations
            
        Returns:
            Dictionary containing detailed processing results:
            - source: Original file path as string
            - target: Final target path as string
            - category: Classification category (e.g., 'documents', 'images')
            - confidence: Classification confidence score (0.0-1.0)
            - moved: Boolean indicating if file was actually moved
            - dry_run: Boolean indicating if this was a simulation
        
        Raises:
            PermissionError: If file cannot be moved due to permissions
            OSError: If filesystem operation fails
        """
        # Step 1: Classify the file using AI-powered classification engine
        # This determines the target category (documents, images, etc.)
        classification = self.classifier.classify_file(file_path)
        
        # Step 2: Construct target path based on classification
        # Creates category-specific subdirectory under target base
        target_dir = target_base / classification['category']
        target_path = target_dir / file_path.name
        
        # Step 3: Handle potential naming conflicts
        # Ensures unique filenames by appending numbers if necessary
        target_path = self._resolve_naming_conflict(target_path)
        
        # Step 4: Prepare result dictionary with operation details
        result = {
            'source': str(file_path),           # Original file location
            'target': str(target_path),         # Final target location
            'category': classification['category'],  # File category from classification
            'confidence': classification['confidence'],  # AI confidence score
            'moved': False,                     # Initially false, updated if file is moved
            'dry_run': dry_run                  # Indicates simulation mode
        }
        
        # Step 5: Perform actual file operations (unless dry run)
        if not dry_run:
            # Ensure target directory structure exists
            # Creates parent directories recursively if they don't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute atomic file move operation
            # rename() is atomic and handles cross-filesystem moves
            file_path.rename(target_path)
            
            # Update result and statistics to reflect successful move
            result['moved'] = True
            self.stats['files_moved'] += 1
            
        return result    
    def _resolve_naming_conflict(self, target_path: Path) -> Path:
        """
        Resolve naming conflicts by appending incremental numbers to filenames.
        
        When a file with the same name already exists at the target location,
        this method generates a unique filename by appending a number suffix.
        Uses pattern: "filename_1.ext", "filename_2.ext", etc.
        
        Args:
            target_path: Proposed target path that may conflict with existing file
            
        Returns:
            Path object with guaranteed unique filename in target directory
            
        Examples:
            If "document.pdf" exists, returns "document_1.pdf"
            If "document_1.pdf" also exists, returns "document_2.pdf"
            
        Note:
            This method performs filesystem checks and may be I/O intensive
            for directories with many naming conflicts.
        """
        # Fast path: if no conflict exists, return original path
        if not target_path.exists():
            return target_path
            
        # Extract filename components for conflict resolution
        base = target_path.stem          # Filename without extension
        suffix = target_path.suffix      # File extension including dot
        parent = target_path.parent      # Parent directory
        
        # Increment counter until we find a unique filename
        counter = 1
        while True:
            # Generate new filename with counter suffix
            # Format: "basename_counter.extension"
            new_name = f"{base}_{counter}{suffix}"
            new_path = parent / new_name
            
            # Check if this generated filename is available
            if not new_path.exists():
                return new_path
                
            # Continue to next counter value
            # Note: This loop will eventually terminate as filesystem
            # filename limits will prevent infinite conflicts
            counter += 1
    
    def _compile_results(self, results: List[Dict]) -> Dict:
        """
        Compile comprehensive results with detailed statistics and performance metrics.
        
        Aggregates individual file processing results into a final summary report
        including success rates, performance metrics, and detailed statistics
        suitable for analysis and reporting.
        
        Args:
            results: List of individual file processing result dictionaries,
                    each containing source, target, category, confidence, and
                    move status information
            
        Returns:
            Comprehensive results dictionary containing:
            - files: List of all individual file processing results
            - statistics: Aggregated performance metrics including:
                - files_processed: Total number of files processed
                - files_moved: Number of files successfully moved
                - errors: Count of processing errors
                - duration_seconds: Total processing time
                - success_rate: Percentage of successful operations (0-100)
                - start_time: Operation start timestamp
                - end_time: Operation completion timestamp
        
        Note:
            Success rate calculation uses max(files_processed, 1) to prevent
            division by zero when no files are processed.
        """
        # Calculate total operation duration in seconds
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # Compile final results with comprehensive statistics
        return {
            'files': results,  # Complete list of individual file results
            'statistics': {
                # Include all base statistics from tracking
                **self.stats,
                
                # Add calculated performance metrics
                'duration_seconds': duration,
                
                # Calculate success rate as percentage
                # Formula: (successful_files / total_files) * 100
                # Uses max() to prevent division by zero edge case
                'success_rate': ((self.stats['files_processed'] - self.stats['errors']) / 
                               max(self.stats['files_processed'], 1)) * 100
            }
        }