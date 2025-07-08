"""
File Scanner Module

Responsible for discovering and filtering files in directories.
Supports various scanning modes and filtering options.

AI Collaboration:
- Extensible design for AI-powered file discovery
- Comprehensive logging for AI analysis
- Configurable filtering for intelligent file selection
"""

import os
from pathlib import Path
from typing import List, Iterator, Optional, Set
import logging

from ..utils.logger import setup_logger


class FileScanner:
    """
    Intelligent file discovery and scanning system.
    
    Provides flexible file discovery with filtering capabilities
    and support for various scanning modes.
    """
    
    def __init__(self, 
                 ignore_hidden: bool = True,
                 ignore_system: bool = True,
                 max_depth: Optional[int] = None):
        """
        Initialize the FileScanner with filtering and scanning configuration.
        
        Sets up the file discovery system with comprehensive filtering options
        to exclude unwanted files and directories from organization operations.
        Configures depth limits and system file exclusions for efficient scanning.
        
        Args:
            ignore_hidden: If True, skips files and directories starting with '.'
                          (e.g., .bashrc, .config/). Prevents processing of hidden
                          system configuration files.
            ignore_system: If True, skips known system files and directories
                          (e.g., .DS_Store, Thumbs.db, __pycache__). Prevents
                          processing of OS and development environment files.
            max_depth: Maximum recursion depth for directory scanning. If None,
                      scans all subdirectories. Use to limit memory usage and
                      scanning time for deep directory structures.
        
        Note:
            System file/directory sets are predefined for common operating systems
            and development environments. This prevents interference with critical
            system files and reduces noise in file organization operations.
        """
        # Initialize logging system for scan operation tracking
        self.logger = setup_logger(__name__)
        
        # Store configuration parameters for filtering logic
        self.ignore_hidden = ignore_hidden
        self.ignore_system = ignore_system
        self.max_depth = max_depth
        
        # Define system directories to ignore during scanning
        # These directories contain system files, caches, or development artifacts
        # that should not be included in file organization operations
        self.system_dirs = {
            '.git',           # Git version control directory
            '.svn',           # Subversion version control directory
            '.hg',            # Mercurial version control directory
            '__pycache__',    # Python bytecode cache directory
            '.pytest_cache', # Pytest cache directory
            'node_modules',   # Node.js dependencies directory
            '.venv',          # Python virtual environment directory
            'venv',           # Python virtual environment directory (alternative name)
            '.env'            # Environment configuration directory
        }
        
        # Define system files to ignore during scanning
        # These files are OS-specific or tool-specific metadata files
        # that should not be processed during file organization
        self.system_files = {
            '.DS_Store',       # macOS directory metadata file
            'Thumbs.db',       # Windows thumbnail cache file
            '.gitignore',      # Git ignore rules file
            '.gitattributes',  # Git attributes file
            'desktop.ini',     # Windows desktop configuration file
            '.localized'       # macOS localization marker file
        }
        
        self.logger.info("FileScanner initialized successfully")
    
    def scan_directory(self, path: Path, recursive: bool = True) -> List[Path]:
        """
        Scan directory for files using configured filtering and depth controls.
        
        This is the main entry point for file discovery operations. It validates
        the target directory and delegates to appropriate scanning methods based
        on the recursion mode requested.
        
        Args:
            path: Directory path to scan. Must exist and be accessible.
            recursive: If True, scans subdirectories recursively up to max_depth.
                      If False, scans only the immediate directory contents.
            
        Returns:
            List of Path objects representing files found that pass all filters.
            Returns empty list if directory doesn't exist or is inaccessible.
        
        Raises:
            None - All errors are logged and handled gracefully with empty results.
        
        Note:
            Applies all configured filters (hidden files, system files) during
            scanning. Files are returned in discovery order, not sorted.
        """
        # Ensure we have a Path object for consistent operations
        path = Path(path)
        
        # Validate directory existence before attempting to scan
        if not path.exists():
            self.logger.error(f"Directory does not exist: {path}")
            return []
            
        # Validate that the path is actually a directory
        if not path.is_dir():
            self.logger.error(f"Path is not a directory: {path}")
            return []
            
        # Log scan initiation for monitoring and debugging
        self.logger.info(f"Scanning directory: {path}")
        
        # Select appropriate scanning strategy based on recursion mode
        files = []
        if recursive:
            # Use recursive scanning with depth control
            files = list(self._scan_recursive(path, 0))
        else:
            # Use single-level scanning for immediate contents only
            files = list(self._scan_single_level(path))
            
        # Log scan results for monitoring and debugging
        self.logger.info(f"Found {len(files)} files in {path}")
        return files    
    def _scan_single_level(self, path: Path) -> Iterator[Path]:
        """
        Scan a single directory level for files without recursion.
        
        Efficiently scans only the immediate contents of a directory,
        filtering files based on configured rules. Uses generator pattern
        for memory efficiency with large directories.
        
        Args:
            path: Directory path to scan for immediate file contents
            
        Yields:
            Path objects for files that pass all filtering criteria
        
        Note:
            This method handles permission errors gracefully by logging warnings
            and continuing operation. Other errors are logged as errors but don't
            stop the scanning process.
        """
        try:
            # Iterate through immediate directory contents
            for item in path.iterdir():
                # Check if item is a file and passes filtering criteria
                if item.is_file() and self._should_include_file(item):
                    yield item
                    
        except PermissionError:
            # Log permission issues but continue scanning
            # This allows partial scanning when some directories are restricted
            self.logger.warning(f"Permission denied scanning: {path}")
            
        except Exception as e:
            # Log unexpected errors but continue scanning
            # This ensures robust operation even with filesystem issues
            self.logger.error(f"Error scanning {path}: {e}")
    
    def _scan_recursive(self, path: Path, current_depth: int) -> Iterator[Path]:
        """
        Recursively scan directories for files with depth control and filtering.
        
        Implements depth-first traversal of directory structure while respecting
        configured depth limits and filtering rules. Handles both files and
        subdirectories appropriately, applying filters at each level.
        
        Args:
            path: Directory path to scan recursively
            current_depth: Current recursion depth level (0 = root directory)
            
        Yields:
            Path objects for files found at current level and all subdirectories
            that pass filtering criteria
        
        Note:
            Depth checking prevents infinite recursion and controls memory usage.
            Permission errors are handled gracefully to allow partial scanning.
            Uses 'yield from' for efficient generator delegation.
        """
        # Check depth limit to prevent excessive recursion
        # This protects against deep directory structures and infinite loops
        if self.max_depth is not None and current_depth >= self.max_depth:
            return
            
        try:
            # Iterate through all items in current directory
            for item in path.iterdir():
                
                # Handle files: check if file passes filtering and yield it
                if item.is_file() and self._should_include_file(item):
                    yield item
                    
                # Handle directories: check if directory should be traversed
                elif item.is_dir() and self._should_include_directory(item):
                    # Recursively scan subdirectory with incremented depth
                    # 'yield from' efficiently delegates to recursive generator
                    yield from self._scan_recursive(item, current_depth + 1)
                    
        except PermissionError:
            # Log permission denied but continue with other directories
            # This allows partial scanning when some directories are restricted
            self.logger.warning(f"Permission denied scanning: {path}")
            
        except Exception as e:
            # Log unexpected errors but continue scanning
            # This ensures robust operation even with filesystem issues
            self.logger.error(f"Error scanning {path}: {e}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be included based on configured filters.
        
        Applies configured filtering rules to determine whether a file should
        be included in scanning results. Evaluates hidden file rules and
        system file exclusions to prevent processing of unwanted files.
        
        Args:
            file_path: Path object representing the file to evaluate
            
        Returns:
            True if file passes all filters and should be included,
            False if file should be excluded from processing
        
        Filtering Rules:
            1. Hidden files: Excluded if ignore_hidden=True and name starts with '.'
            2. System files: Excluded if ignore_system=True and name in system_files set
            3. Default: Include file if no exclusion rules match
        """
        # Check hidden file filter
        # Hidden files start with '.' and are typically configuration files
        if self.ignore_hidden and file_path.name.startswith('.'):
            return False
            
        # Check system file filter
        # System files are OS-specific metadata files that should not be organized
        if self.ignore_system and file_path.name in self.system_files:
            return False
            
        # File passes all filters - include it in results
        return True
    
    def _should_include_directory(self, dir_path: Path) -> bool:
        """
        Determine if a directory should be traversed during recursive scanning.
        
        Applies configured filtering rules to determine whether a directory
        should be recursively scanned for files. Evaluates hidden directory
        rules and system directory exclusions to prevent traversal of
        directories that should not be processed.
        
        Args:
            dir_path: Path object representing the directory to evaluate
            
        Returns:
            True if directory passes all filters and should be traversed,
            False if directory should be excluded from recursive scanning
        
        Filtering Rules:
            1. Hidden directories: Excluded if ignore_hidden=True and name starts with '.'
            2. System directories: Excluded if ignore_system=True and name in system_dirs set
            3. Default: Include directory if no exclusion rules match
        
        Note:
            This filtering is crucial for preventing traversal of version control
            directories, cache directories, and other system-managed directories
            that should not be included in file organization operations.
        """
        # Check hidden directory filter
        # Hidden directories start with '.' and are typically system/config directories
        if self.ignore_hidden and dir_path.name.startswith('.'):
            return False
            
        # Check system directory filter
        # System directories contain development artifacts, caches, or version control data
        if self.ignore_system and dir_path.name in self.system_dirs:
            return False
            
        # Directory passes all filters - include it in traversal
        return True