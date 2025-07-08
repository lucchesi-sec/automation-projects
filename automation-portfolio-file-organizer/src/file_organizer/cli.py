"""
Command Line Interface for Smart File Organizer

Provides a user-friendly CLI for file organization operations
with various options and modes.

AI Collaboration:
- CLI designed for both manual and automated use
- Comprehensive output for AI analysis and monitoring
- Interactive mode for AI-assisted file organization
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core.organizer import FileOrganizer
from .utils.logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser for the Smart File Organizer.
    
    Sets up a comprehensive argument parser with all CLI options, help text,
    and usage examples. Designed for both interactive use and scripting/automation.
    
    Returns:
        Configured ArgumentParser instance ready for parsing command-line arguments
    
    Note:
        Uses RawDescriptionHelpFormatter to preserve formatting in the epilog
        examples section. The %(prog)s placeholder is automatically replaced
        with the actual program name by argparse.
    """
    # Create parser with comprehensive description and formatted examples
    parser = argparse.ArgumentParser(
        description="Smart File Organizer - AI-powered file management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/organize                    # Organize files in-place
  %(prog)s /source /target                      # Organize to different directory
  %(prog)s /path --dry-run                      # Preview organization
  %(prog)s /path --config custom.yaml          # Use custom configuration
  %(prog)s /path --recursive --max-depth 3     # Limited recursive scan
        """
    )
    
    # Required arguments
    parser.add_argument(
        "source",
        help="Source directory to organize"
    )
    
    parser.add_argument(
        "target",
        nargs="?",
        help="Target directory for organized files (optional)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview organization without moving files"
    )
    
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively organize subdirectories"
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        help="Maximum depth for recursive organization"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity (use -v, -vv, or -vvv)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file path"
    )
    
    return parser


def main():
    """
    Main entry point for the Smart File Organizer CLI application.
    
    This function serves as the central orchestrator for the command-line interface,
    handling argument parsing, logging configuration, file organization execution,
    and comprehensive error management. It provides a complete user experience
    with detailed feedback and appropriate exit codes.
    
    The function implements a robust workflow:
    1. Command-line argument parsing with validation
    2. Logging system configuration based on verbosity levels
    3. Source directory validation and error handling
    4. File organization execution with progress tracking
    5. Results display with statistics and performance metrics
    6. Appropriate exit codes for automation and scripting
    
    Verbosity Levels:
        -q/--quiet: Only error messages (ERROR level)
        Default: Standard warnings and errors (WARNING level)
        -v: Informational messages (INFO level)
        -vv/-vvv: Debug messages with full details (DEBUG level)
    
    Exit Codes:
        0: Success - All files processed without errors
        1: Errors occurred during processing
        130: User interrupted operation (Ctrl+C)
        1: Unexpected error or system failure
    
    Raises:
        SystemExit: Always called with appropriate exit code
        
    Note:
        This function never returns normally - it always exits via sys.exit()
        with an appropriate code for shell scripting and automation integration.
    """
    # Phase 1: Command-Line Argument Processing
    # Parse and validate all command-line arguments using configured parser
    parser = create_parser()
    args = parser.parse_args()
    
    # Phase 2: Logging Configuration Based on Verbosity
    # Map CLI verbosity flags to Python logging levels for consistent output control
    # The verbosity system allows users to control the amount of information displayed
    if args.quiet:
        # Quiet mode: Only show critical errors, suppress all other output
        log_level = "ERROR"
    elif args.verbose == 1:
        # Single -v flag: Show informational messages about organization progress
        log_level = "INFO"
    elif args.verbose >= 2:
        # Multiple -v flags (-vv, -vvv): Show detailed debug information
        # Includes classification details, file processing steps, and performance metrics
        log_level = "DEBUG"
    else:
        # Default mode: Show warnings and errors only
        # Balances useful information with clean output for typical usage
        log_level = "WARNING"
    
    # Initialize logging system with configured level and optional file output
    # This provides consistent logging across all components with proper formatting
    logger = setup_logger(
        name=__name__,
        level=log_level,
        log_file=args.log_file  # Optional log file for persistent logging
    )
    
    try:
        # Phase 3: Source Directory Validation
        # Comprehensive validation ensures early failure for invalid inputs
        # This prevents wasted processing time and provides clear error messages
        source_path = Path(args.source)
        
        # Check if source path exists in the filesystem
        if not source_path.exists():
            logger.error(f"Source directory does not exist: {source_path}")
            sys.exit(1)  # Exit with error code for shell scripting
        
        # Verify that source path is actually a directory (not a file)
        if not source_path.is_dir():
            logger.error(f"Source path is not a directory: {source_path}")
            sys.exit(1)  # Exit with error code for shell scripting
        
        # Phase 4: File Organization System Initialization
        # Create the main organizer instance with optional custom configuration
        # Configuration loading is handled internally with proper error handling
        organizer = FileOrganizer(
            config_path=args.config  # Optional path to custom YAML configuration
        )
        
        # Phase 5: Dynamic Configuration Override
        # Allow CLI arguments to override default configuration settings
        # This provides command-line control over configuration-driven behavior
        if args.recursive:
            # Enable recursive directory scanning when requested
            # Override default configuration with CLI preference
            organizer.config.get('scanner', {})['recursive'] = True
        
        if args.max_depth:
            # Set maximum recursion depth to prevent infinite loops
            # Useful for limiting processing in deep directory structures
            organizer.config.get('scanner', {})['max_depth'] = args.max_depth
        
        # Phase 6: Execute File Organization Operation
        # This is the main processing phase that coordinates all file operations
        # Includes classification, organization, and comprehensive result tracking
        result = organizer.organize_directory(
            source_path=str(source_path),    # Convert Path back to string for internal API
            target_path=args.target,         # Optional target directory (None = in-place)
            dry_run=args.dry_run            # Simulation mode for safe preview
        )
        
        # Phase 7: Results Display and User Feedback
        # Provide comprehensive feedback unless in quiet mode
        # Format results for both human consumption and automation parsing
        if not args.quiet:
            # Display formatted results header
            print("\n" + "="*50)
            print("FILE ORGANIZATION RESULTS")
            print("="*50)
            
            # Extract and display core statistics
            stats = result.get('statistics', {})
            print(f"Files processed: {stats.get('files_processed', 0)}")
            print(f"Files moved: {stats.get('files_moved', 0)}")
            print(f"Files skipped: {stats.get('files_skipped', 0)}")
            print(f"Errors: {stats.get('errors', 0)}")
            
            # Show dry-run disclaimer if applicable
            if args.dry_run:
                print("\n(DRY RUN - No files were actually moved)")
            
            # Show extended information in verbose mode
            if args.verbose:
                # Display performance metrics for analysis
                print(f"\nExecution time: {stats.get('execution_time', 0):.2f} seconds")
                print(f"Categories processed: {', '.join(stats.get('categories_processed', []))}")
        
        # Phase 8: Exit Code Determination
        # Return appropriate exit codes for shell scripting and automation
        # This allows other programs to determine success/failure programmatically
        if result.get('statistics', {}).get('errors', 0) > 0:
            # Exit with error code if any files failed to process
            # This indicates partial failure and requires user attention
            sys.exit(1)
        else:
            # Exit with success code if all files processed successfully
            # This indicates complete success and safe automation continuation
            sys.exit(0)
    
    except KeyboardInterrupt:
        # Handle user interruption (Ctrl+C) gracefully
        # This is common during long-running operations or when users change their mind
        logger.info("Operation cancelled by user")
        sys.exit(130)  # Standard exit code for signal interruption (128 + SIGINT)
        
    except Exception as e:
        # Handle all other unexpected errors with comprehensive logging
        # This ensures no errors go unnoticed while providing useful debugging info
        logger.error(f"Unexpected error: {e}")
        
        # In debug mode, provide full stack trace for detailed error analysis
        # This helps developers and advanced users diagnose complex issues
        if args.verbose >= 2:
            import traceback
            traceback.print_exc()  # Print full stack trace to stderr
            
        # Exit with generic error code to indicate system failure
        sys.exit(1)


if __name__ == "__main__":
    main()