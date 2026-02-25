#!/usr/bin/env python3
"""
Vault Watcher - Production Ready

Continuously monitors AI_Employee_Vault/Inbox folder for new .md files.
When detected, logs to logs/action.log and triggers AI Processing workflow.
Uses file tracking to avoid processing duplicates.
Runs every 10-30 seconds (randomized interval).

Usage:
    python scripts/watch_inbox.py

Features:
- Lightweight & production-ready
- Duplicate detection via processed_files.txt
- Randomized check interval (10-30 seconds)
- Graceful shutdown on Ctrl+C
- Comprehensive error logging
- AI Processing workflow integration
"""

import os
import sys
import time
import random
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Set, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent

# Define folder paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "Logs"
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"

# File paths
PROCESSED_TRACKER_FILE = LOGS_DIR / "processed_files.txt"
ACTION_LOG_FILE = LOGS_DIR / "action.log"
ERROR_LOG_FILE = LOGS_DIR / "watcher_errors.log"

# Timing configuration (in seconds)
MIN_CHECK_INTERVAL = 10
MAX_CHECK_INTERVAL = 30

# AI Employee script path
AI_EMPLOYEE_SCRIPT = BASE_DIR / "ai_employee.py"


# =============================================================================
# WATCHER STATE
# =============================================================================

class WatcherState:
    """Manages watcher state and graceful shutdown"""
    
    def __init__(self):
        self.running = True
        self.start_time: Optional[datetime] = None
        self.files_processed = 0
        self.detections_logged = 0
        
    def start(self):
        """Mark watcher as started"""
        self.running = True
        self.start_time = datetime.now()
        
    def stop(self):
        """Mark watcher as stopped"""
        self.running = False
        
    def uptime(self) -> str:
        """Get human-readable uptime string"""
        if not self.start_time:
            return "0 seconds"
        delta = datetime.now() - self.start_time
        total_seconds = int(delta.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        if minutes > 0:
            return f"{minutes} minutes {seconds} seconds"
        return f"{seconds} seconds"


# Global state instance
state = WatcherState()


# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def ensure_folders() -> None:
    """Ensure all required folders exist"""
    for folder in [INBOX_DIR, LOGS_DIR, NEEDS_ACTION_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def log_action(message: str) -> None:
    """Log an action to action.log"""
    try:
        ensure_folders()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(ACTION_LOG_FILE, "a") as f:
            f.write(log_entry)
            
    except Exception as e:
        log_error(f"Failed to write action log: {e}")


def log_error(message: str) -> None:
    """Log an error to watcher_errors.log"""
    try:
        ensure_folders()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] ERROR: {message}\n"
        
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(error_entry)
            
    except Exception as e:
        # If we can't log to file, print to stderr
        print(f"[CRITICAL] Failed to log error: {e}", file=sys.stderr)


def load_processed_files() -> Set[str]:
    """Load the set of already processed filenames"""
    try:
        if PROCESSED_TRACKER_FILE.exists():
            with open(PROCESSED_TRACKER_FILE, "r") as f:
                return set(line.strip() for line in f if line.strip())
    except Exception as e:
        log_error(f"Failed to load processed files tracker: {e}")
    return set()


def save_processed_file(filename: str, processed_set: Set[str]) -> None:
    """Save a filename to the processed tracker"""
    try:
        with open(PROCESSED_TRACKER_FILE, "a") as f:
            f.write(filename + "\n")
        processed_set.add(filename)
    except Exception as e:
        log_error(f"Failed to save processed file '{filename}': {e}")


# =============================================================================
# AI PROCESSING WORKFLOW
# =============================================================================

def trigger_ai_processing() -> bool:
    """
    Trigger the AI Processing workflow.
    Same as running: python ai_employee.py --once
    
    Returns:
        bool: True if triggered successfully, False otherwise
    """
    try:
        if not AI_EMPLOYEE_SCRIPT.exists():
            log_error(f"AI Employee script not found: {AI_EMPLOYEE_SCRIPT}")
            return False
        
        # Run the AI employee script in once mode
        result = subprocess.run(
            [sys.executable, str(AI_EMPLOYEE_SCRIPT), "--once"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            log_action(f"AI Processing completed successfully")
            return True
        else:
            log_error(f"AI Processing failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_error("AI Processing timed out after 5 minutes")
        return False
    except Exception as e:
        log_error(f"Failed to trigger AI Processing: {e}")
        return False


# =============================================================================
# FILE MONITORING
# =============================================================================

def get_inbox_md_files() -> Set[str]:
    """Get all .md files in the Inbox folder"""
    try:
        if not INBOX_DIR.exists():
            return set()
        
        return {f.name for f in INBOX_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".md"}
    except Exception as e:
        log_error(f"Failed to read Inbox folder: {e}")
        return set()


def check_for_new_files(processed_files: Set[str]) -> list:
    """
    Check for new .md files in Inbox that haven't been processed.
    
    Returns:
        list: List of new filenames to process
    """
    try:
        current_files = get_inbox_md_files()
        new_files = list(current_files - processed_files)
        return sorted(new_files)
    except Exception as e:
        log_error(f"Error checking for new files: {e}")
        return []


def process_new_file(filename: str, processed_files: Set[str]) -> None:
    """
    Process a newly detected file:
    1. Log detection
    2. Add to processed tracker
    3. Trigger AI Processing workflow
    
    Args:
        filename: Name of the file to process
        processed_files: Set of already processed filenames
    """
    try:
        # Log detection
        log_action(f"DETECTED: {filename} - Triggering AI Processing")
        state.detections_logged += 1
        
        # Add to processed tracker immediately to avoid duplicates
        save_processed_file(filename, processed_files)
        log_action(f"PROCESSED: {filename} - Added to tracker")
        
        # Trigger AI Processing workflow
        if trigger_ai_processing():
            state.files_processed += 1
        else:
            log_error(f"AI Processing failed for: {filename}")
            
    except Exception as e:
        log_error(f"Error processing file '{filename}': {e}")


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_action(f"WATCHER_STOPPED - Received signal {signum}")
    state.stop()


def setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# =============================================================================
# MAIN WATCHER LOOP
# =============================================================================

def print_startup_banner() -> None:
    """Print watcher startup banner"""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                    👁️ Vault Watcher                       ║
╠══════════════════════════════════════════════════════════╣
║  Monitoring: {str(INBOX_DIR.relative_to(BASE_DIR)):<42} ║
║  Check Interval: {MIN_CHECK_INTERVAL}-{MAX_CHECK_INTERVAL} seconds (randomized){" " * 18} ║
║  Processed Tracker: {str(PROCESSED_TRACKER_FILE.relative_to(BASE_DIR)):<33} ║
║  Action Log: {str(ACTION_LOG_FILE.relative_to(BASE_DIR)):<42} ║
╚══════════════════════════════════════════════════════════╝

Press Ctrl+C to stop watching
"""
    print(banner)


def print_shutdown_summary() -> None:
    """Print shutdown summary"""
    summary = f"""
╔══════════════════════════════════════════════════════════╗
║              ✅ Vault Watcher Stopped                     ║
╠══════════════════════════════════════════════════════════╣
║  Total files processed: {state.files_processed:<31} ║
║  Total detections logged: {state.detections_logged:<29} ║
║  Uptime: {state.uptime():<46} ║
╚══════════════════════════════════════════════════════════╝
"""
    print(summary)


def main() -> None:
    """Main entry point for the vault watcher"""
    # Setup
    ensure_folders()
    setup_signal_handlers()
    state.start()
    
    # Load processed files tracker
    processed_files = load_processed_files()
    
    # Print startup banner
    print_startup_banner()
    log_action(f"WATCHER_STARTED - Monitoring {INBOX_DIR}")
    
    print(f"Loaded {len(processed_files)} previously processed files")
    print()
    
    try:
        # Main monitoring loop
        while state.running:
            try:
                # Check for new .md files
                new_files = check_for_new_files(processed_files)
                
                if new_files:
                    for filename in new_files:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Detected: {filename}")
                        process_new_file(filename, processed_files)
                
                # Randomized sleep interval (10-30 seconds)
                sleep_time = random.randint(MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL)
                time.sleep(sleep_time)
                
            except Exception as e:
                log_error(f"Error in main loop: {e}")
                # Continue running even after errors
                time.sleep(MIN_CHECK_INTERVAL)
                
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        
    finally:
        # Cleanup
        log_action(f"WATCHER_STOPPED - Processed {state.files_processed} files, Uptime: {state.uptime()}")
        print_shutdown_summary()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
