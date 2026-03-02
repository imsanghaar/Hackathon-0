#!/usr/bin/env python3
"""
File Watcher - Bronze Tier

This script monitors the 'Inbox' folder for new files.
When a new file is detected, it creates a corresponding task file
in the 'Needs_Action' folder for review.

Features:
- Checks the Inbox folder every 5 seconds
- Avoids creating duplicate tasks for the same file
- Creates structured markdown task files
- Robust error handling to prevent crashes
"""

import os
import time
import traceback
from datetime import datetime
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.resolve()

# Define folder paths
INBOX_FOLDER = BASE_DIR / "Inbox"
NEEDS_ACTION_FOLDER = BASE_DIR / "Needs_Action"
LOGS_FOLDER = BASE_DIR / "Logs"

# How often to check for new files (in seconds)
CHECK_INTERVAL = 5

# File to track which files have already been processed
PROCESSED_TRACKER_FILE = LOGS_FOLDER / "processed_files.txt"

# File to log any errors that occur during watching
ERROR_LOG_FILE = LOGS_FOLDER / "watcher_errors.log"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_folders_exist():
    """
    Make sure the required folders exist.
    Creates them if they don't already exist.
    
    This ensures the script can run even on first use when
    folders haven't been created yet.
    """
    try:
        INBOX_FOLDER.mkdir(parents=True, exist_ok=True)
        NEEDS_ACTION_FOLDER.mkdir(parents=True, exist_ok=True)
        LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # If we can't create folders, log the error and re-raise
        log_error(f"Failed to create required folders: {e}")
        raise


def log_error(error_message):
    """
    Log an error message to the error log file.
    
    This function writes errors to a separate log file so that
    the main script can continue running without crashing.
    Each error includes a timestamp for debugging.
    
    Args:
        error_message: The error message to log
    """
    try:
        # Ensure the logs folder exists before writing
        LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] {error_message}\n"
        
        # Append the error to the log file
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(error_entry)
            
        print(f"[ERROR] {error_message} (logged to {ERROR_LOG_FILE})")
    except Exception as e:
        # If we can't even log the error, print to console
        print(f"[CRITICAL] Failed to log error: {e}")


def load_processed_files():
    """
    Load the list of files that have already been processed.
    This helps avoid creating duplicate tasks.
    
    Returns:
        set: A set of filenames that have been processed
    """
    try:
        if PROCESSED_TRACKER_FILE.exists():
            with open(PROCESSED_TRACKER_FILE, "r") as f:
                # Read each line and strip whitespace, ignore empty lines
                return set(line.strip() for line in f if line.strip())
    except Exception as e:
        # If we can't load the tracker, start fresh and log the error
        log_error(f"Failed to load processed files tracker: {e}")
    
    return set()


def save_processed_file(filename):
    """
    Add a filename to the processed files tracker.
    
    Args:
        filename: The name of the file that was processed
    """
    try:
        with open(PROCESSED_TRACKER_FILE, "a") as f:
            f.write(filename + "\n")
    except Exception as e:
        # Log the error but don't crash - the task was still created
        log_error(f"Failed to save processed file '{filename}': {e}")


def get_inbox_files():
    """
    Get all files currently in the Inbox folder.
    
    Returns:
        set: A set of filenames in the Inbox
    """
    try:
        if not INBOX_FOLDER.exists():
            return set()
        
        # Get all files (not directories) in the Inbox
        files = set()
        for item in INBOX_FOLDER.iterdir():
            if item.is_file():
                files.add(item.name)
        return files
    except Exception as e:
        # Log the error and return empty set to continue safely
        log_error(f"Failed to read Inbox folder: {e}")
        return set()


def create_task_file(filename):
    """
    Create a new task file in the Needs_Action folder.

    The task file follows the structured template format with:
    - YAML frontmatter containing metadata
    - Clear task title and description
    - Actionable checklist items
    - Notes section for context

    Args:
        filename: The name of the file that triggered this task
    """
    try:
        # Generate a timestamp for when this task was created
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create a safe task filename (replace spaces with underscores, add .md)
        # Example: "my document.pdf" -> "task_my_document.pdf.md"
        safe_name = filename.replace(" ", "_")
        task_filename = f"task_{safe_name}.md"
        task_filepath = NEEDS_ACTION_FOLDER / task_filename

        # Create the task file content using the improved structured format
        # This follows the template defined in Plans/task_template.md
        content = f"""---
type: file_review
status: pending
priority: medium
created_at: {timestamp}
related_files: ["{filename}"]
---

# Task: Review File - {filename}

## Description
A new file was added to the Inbox and requires review.
Please examine the file content and determine the appropriate action.

## Checklist
- [ ] Open and review the file content
- [ ] Identify the file type and purpose
- [ ] Decide what action is needed (archive, process, delete, etc.)

## Notes
- Source: Inbox folder
- Original filename: {filename}
- Detected at: {timestamp}
"""

        # Write the task file
        with open(task_filepath, "w") as f:
            f.write(content)

        print(f"[{timestamp}] Created task for: {filename}")
    except Exception as e:
        # Log the error but don't crash - continue monitoring
        log_error(f"Failed to create task file for '{filename}': {e}")


# =============================================================================
# MAIN WATCHER LOOP
# =============================================================================

def main():
    """
    Main function that runs the file watcher loop.

    This function:
    1. Sets up required folders
    2. Loads previously processed files
    3. Continuously checks for new files every 5 seconds
    4. Creates tasks for any new files found
    
    Error Handling:
    - The main loop is wrapped in try/except to prevent crashes
    - Any errors during file processing are logged and skipped
    - The script continues running even if individual operations fail
    """
    print("=" * 50)
    print("Bronze Tier File Watcher Started")
    print(f"Monitoring: {INBOX_FOLDER}")
    print(f"Tasks created in: {NEEDS_ACTION_FOLDER}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    # Ensure all required folders exist
    # This will create Inbox, Needs_Action, and Logs folders if missing
    ensure_folders_exist()

    # Load the list of files we've already processed
    processed_files = load_processed_files()
    print(f"Previously processed files: {len(processed_files)}")
    print()

    try:
        # Main monitoring loop - runs forever until stopped
        while True:
            try:
                # Get all files currently in the Inbox
                current_files = get_inbox_files()

                # Check each file to see if it's new
                for filename in current_files:
                    if filename not in processed_files:
                        # This is a new file! Create a task for it
                        create_task_file(filename)

                        # Mark this file as processed so we don't create duplicates
                        processed_files.add(filename)
                        save_processed_file(filename)

                # Wait before checking again
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                # Catch any error in the loop and log it
                # This prevents the script from crashing on unexpected errors
                log_error(f"Error in main loop: {e}")
                # Wait a bit before retrying to avoid rapid error logging
                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        # User pressed Ctrl+C - exit gracefully
        print("\n\nWatcher stopped by user.")
    except Exception as e:
        # Catch any other unexpected to prevent crash
        log_error(f"Unexpected error in main function: {e}\n{traceback.format_exc()}")
        print("\n\nWatcher encountered an error. Check Logs/watcher_errors.log for details.")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
