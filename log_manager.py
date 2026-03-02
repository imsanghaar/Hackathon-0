#!/usr/bin/env python3
"""
Log Manager - Bronze Tier

This script manages log files to prevent them from growing too large.
When a log file exceeds the size limit, it is archived with a timestamp
and a fresh empty log file is created.

Features:
- Checks log file sizes
- Archives large files with timestamps
- Creates fresh log files automatically
- Simple and beginner-friendly code
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.resolve()

# Define paths to log files that need management
LOG_FILES = [
    BASE_DIR / "System_Log.md",
    BASE_DIR / "Logs" / "watcher_errors.log",
]

# Maximum file size in bytes before archiving (1 MB = 1024 * 1024 bytes)
MAX_FILE_SIZE = 1 * 1024 * 1024


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_file_size(filepath):
    """
    Get the size of a file in bytes.
    
    Args:
        filepath: Path to the file
        
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    """
    if filepath.exists():
        return filepath.stat().st_size
    return 0


def format_size(size_bytes):
    """
    Convert bytes to a human-readable format (KB, MB, etc.).
    
    This helps when printing file sizes for the user.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Human-readable size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def archive_log_file(filepath):
    """
    Archive a log file by renaming it with a timestamp.
    
    The original file is renamed to include the current date and time,
    preserving the log data while allowing a fresh file to be created.
    
    Example:
        System_Log.md -> System_Log_2026-01-29_14-30-00.md
        watcher_errors.log -> watcher_errors_2026-01-29_14-30-00.log
    
    Args:
        filepath: Path to the log file to archive
    """
    # Generate timestamp for the archive filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Get the file stem (name without extension) and suffix (extension)
    stem = filepath.stem
    suffix = filepath.suffix
    
    # Create new archived filename with timestamp
    # Example: "System_Log.md" -> "System_Log_2026-01-29_14-30-00.md"
    archived_name = f"{stem}_{timestamp}{suffix}"
    archived_path = filepath.parent / archived_name
    
    # Rename the file (move/rename operation)
    filepath.rename(archived_path)
    
    print(f"Archived: {filepath.name} -> {archived_name}")
    
    return archived_path


def create_fresh_log(filepath):
    """
    Create a new empty log file with proper initial content.
    
    The content depends on the type of log file:
    - System_Log.md: Gets markdown header and activity log table
    - watcher_errors.log: Starts empty (plain text log)
    
    Args:
        filepath: Path to the log file to create
    """
    if filepath.name == "System_Log.md":
        # Create structured markdown content for system log
        content = """# System Log

## Activity Log

| Date | Action | Details |
|------|--------|---------|
|      |        |         |
"""
    elif filepath.name == "watcher_errors.log":
        # Plain text error log - start with a header comment
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"# Error Log Started: {timestamp}\n"
    else:
        # For any other log files, start empty
        content = ""
    
    # Write the fresh content to the file
    with open(filepath, "w") as f:
        f.write(content)
    
    print(f"Created fresh log: {filepath.name}")


def check_and_rotate_log(filepath):
    """
    Check if a log file needs rotation and perform it if necessary.
    
    This function:
    1. Checks if the file exists
    2. Checks if the file exceeds the size limit
    3. If yes, archives the file and creates a fresh one
    
    Args:
        filepath: Path to the log file to check
        
    Returns:
        bool: True if the file was rotated, False otherwise
    """
    # Skip if file doesn't exist
    if not filepath.exists():
        print(f"Skipping (not found): {filepath.name}")
        return False
    
    # Get current file size
    current_size = get_file_size(filepath)
    
    # Check if file exceeds the maximum size
    if current_size > MAX_FILE_SIZE:
        print(f"\n[ROTATE] {filepath.name} ({format_size(current_size)} > {format_size(MAX_FILE_SIZE)})")
        
        # Archive the current log file
        archive_log_file(filepath)
        
        # Create a fresh empty log file
        create_fresh_log(filepath)
        
        return True
    else:
        print(f"[OK] {filepath.name} ({format_size(current_size)})")
        return False


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """
    Main function that runs the log management process.
    
    This function:
    1. Prints status header
    2. Checks each configured log file
    3. Rotates any files that exceed the size limit
    4. Prints summary
    """
    print("=" * 50)
    print("Log Manager - Bronze Tier")
    print(f"Max file size: {format_size(MAX_FILE_SIZE)}")
    print("=" * 50)
    print()
    
    # Track how many files were rotated
    rotated_count = 0
    
    # Check each log file in the list
    for log_path in LOG_FILES:
        if check_and_rotate_log(log_path):
            rotated_count += 1
    
    # Print summary
    print()
    print("=" * 50)
    print(f"Log management complete. Rotated {rotated_count} file(s).")
    print("=" * 50)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
