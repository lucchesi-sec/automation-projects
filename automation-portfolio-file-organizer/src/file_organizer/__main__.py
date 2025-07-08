"""
Entry point for running the file organizer as a module.

This allows the package to be executed with:
    python -m file_organizer
"""

from .cli import main

if __name__ == "__main__":
    main()