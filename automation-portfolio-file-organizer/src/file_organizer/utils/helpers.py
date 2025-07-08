"""
Helper Utilities

Common utility functions used throughout the Smart File Organizer.
Provides file handling, formatting, and data processing utilities.

AI Collaboration:
- Utility functions designed for AI-enhanced file processing
- Data formatting for AI model inputs
- Hash generation for duplicate detection and ML training
"""

import hashlib
import re
from pathlib import Path
from typing import Optional


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., '1.5 MB')
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def get_file_hash(file_path: Path, algorithm: str = "md5") -> Optional[str]:
    """
    Generate hash for a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of the file hash, or None if error
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    except Exception:
        return None


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename for filesystem
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    # Truncate if too long (most filesystems limit to 255 characters)
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_len] + ('.' + ext if ext else '')
    
    return filename