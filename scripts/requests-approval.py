#!/usr/bin/env python3
"""
Human Approval Checker - Production Ready

Monitors AI_Employee_Vault/Needs_Action folder for pending approvals.
Blocks execution until human writes Approved/Rejected in file.
Renames files with .approved, .rejected, .timeout suffix based on result.
Timeout after configurable duration (default 2 hours).
Logs all actions to logs/action.log.

Usage:
    python scripts/requests-approval.py                    # Check all pending
    python scripts/requests-approval.py --timeout 3600     # Custom timeout
    python scripts/requests-approval.py --file <filename>  # Check specific file
    python scripts/requests-approval.py --dry-run          # Preview only
    python scripts/requests-approval.py --watch            # Continuous monitoring

Features:
- Configurable timeout (default 2 hours)
- Automatic file renaming based on approval status
- Continuous monitoring mode
- Comprehensive action logging
- Idempotent processing
"""

import os
import sys
import argparse
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent

# Define folder paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# File paths
ACTION_LOG_FILE = LOGS_DIR / "action.log"
ERROR_LOG_FILE = LOGS_DIR / "watcher_errors.log"
APPROVAL_TRACKER_FILE = LOGS_DIR / "approval_tracker.txt"

# Default timeout: 2 hours (7200 seconds)
DEFAULT_TIMEOUT_SECONDS = 7200

# Status suffixes
STATUS_APPROVED = ".approved"
STATUS_REJECTED = ".rejected"
STATUS_TIMEOUT = ".timeout"
STATUS_PENDING = ".pending"


# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def ensure_folders() -> None:
    """Ensure all required folders exist"""
    for folder in [NEEDS_ACTION_DIR, DONE_DIR, LOGS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def log_action(message: str) -> None:
    """Log an action to action.log"""
    try:
        ensure_folders()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] APPROVAL: {message}\n"
        
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
        print(f"[CRITICAL] Failed to log error: {e}", file=sys.stderr)


# =============================================================================
# TRACKER UTILITIES
# =============================================================================

def load_processed_approvals() -> Set[str]:
    """Load the set of already processed approval filenames"""
    try:
        if APPROVAL_TRACKER_FILE.exists():
            with open(APPROVAL_TRACKER_FILE, "r") as f:
                return set(line.strip() for line in f if line.strip())
    except Exception as e:
        log_error(f"Failed to load approval tracker: {e}")
    return set()


def save_processed_approval(filename: str) -> None:
    """Save a filename to the processed approvals tracker"""
    try:
        ensure_folders()
        with open(APPROVAL_TRACKER_FILE, "a") as f:
            f.write(filename + "\n")
    except Exception as e:
        log_error(f"Failed to save processed approval '{filename}': {e}")


# =============================================================================
# FILE ANALYSIS
# =============================================================================

def parse_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML frontmatter from markdown content"""
    frontmatter = {}
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_content = parts[1].strip()
            for line in fm_content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    frontmatter[key] = value
    
    return frontmatter


def get_file_creation_time(filepath: Path) -> datetime:
    """Get file creation time (or modification time as fallback)"""
    try:
        # Try to get creation time
        stat = filepath.stat()
        # On Linux, st_ctime is change time, on Windows it's creation time
        # Use modification time as a more reliable indicator
        return datetime.fromtimestamp(stat.st_mtime)
    except Exception as e:
        log_error(f"Failed to get file time for '{filepath.name}': {e}")
        return datetime.now()


def check_approval_status(content: str) -> Tuple[str, Optional[str]]:
    """
    Check if file has been approved or rejected by human.
    
    Returns:
        tuple: (status, reviewer_name)
            status: 'approved', 'rejected', or 'pending'
            reviewer_name: Name of reviewer if found, None otherwise
    """
    # Look for approval/rejection markers in content
    # Pattern 1: **Status:** Approved/Rejected
    status_pattern = r'\*\*Status:\*\*\s*(Approved|Rejected|Pending)'
    match = re.search(status_pattern, content, re.IGNORECASE)
    
    if match:
        status = match.group(1).lower()
        # Try to find reviewer name
        reviewer_pattern = r'\*\*Reviewed by:\*\*\s*(.+?)(?:\n|$)'
        reviewer_match = re.search(reviewer_pattern, content, re.IGNORECASE)
        reviewer = reviewer_match.group(1).strip() if reviewer_match else None
        return status, reviewer
    
    # Pattern 2: ## Decision section with Status: Approved/Rejected
    decision_pattern = r'##\s*Decision.*?Status:\s*(Approved|Rejected|Pending)'
    match = re.search(decision_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        status = match.group(1).lower()
        return status, None
    
    # Pattern 3: Simple text markers
    if re.search(r'\bApproved\b', content, re.IGNORECASE) and not re.search(r'\bPending\b', content, re.IGNORECASE):
        return 'approved', None
    
    if re.search(r'\bRejected\b', content, re.IGNORECASE):
        return 'rejected', None
    
    return 'pending', None


def is_pending_approval(filepath: Path) -> bool:
    """Check if a file is pending approval"""
    try:
        # Skip already processed files
        if filepath.suffix in [STATUS_APPROVED, STATUS_REJECTED, STATUS_TIMEOUT]:
            return False
        
        # Skip .pending suffix files
        if filepath.name.endswith(STATUS_PENDING):
            return True
        
        # Check frontmatter for pending_approval status
        content = filepath.read_text(encoding='utf-8')
        frontmatter = parse_frontmatter(content)
        
        status = frontmatter.get('status', '')
        approval_required = frontmatter.get('approval_required', '')
        
        return status == 'pending_approval' or approval_required.lower() == 'true'
        
    except Exception as e:
        log_error(f"Failed to check approval status for '{filepath.name}': {e}")
        return False


# =============================================================================
# FILE OPERATIONS
# =============================================================================

def rename_file_with_status(filepath: Path, status: str, dry_run: bool = False) -> bool:
    """
    Rename file with status suffix.
    
    Args:
        filepath: Path to file to rename
        status: One of 'approved', 'rejected', 'timeout'
        dry_run: If True, don't actually rename
        
    Returns:
        bool: True if successful
    """
    try:
        suffix_map = {
            'approved': STATUS_APPROVED,
            'rejected': STATUS_REJECTED,
            'timeout': STATUS_TIMEOUT
        }
        
        suffix = suffix_map.get(status.lower())
        if not suffix:
            log_error(f"Invalid status for rename: {status}")
            return False
        
        # Create new filename
        new_name = filepath.name + suffix
        new_path = filepath.parent / new_name
        
        if dry_run:
            print(f"[DRY-RUN] Would rename: {filepath.name} → {new_name}")
            log_action(f"Would rename {filepath.name} → {new_name}")
            return True
        
        # Rename the file
        filepath.rename(new_path)
        log_action(f"Renamed {filepath.name} → {new_name}")
        print(f"[{status.upper()}] {filepath.name} → {new_name}")
        return True
        
    except Exception as e:
        log_error(f"Failed to rename '{filepath.name}': {e}")
        return False


def update_file_status(filepath: Path, new_status: str, dry_run: bool = False) -> bool:
    """
    Update the status in file frontmatter.
    
    Args:
        filepath: Path to file to update
        new_status: New status value
        dry_run: If True, don't actually write
        
    Returns:
        bool: True if successful
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Update frontmatter status
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_content = parts[1].strip()
                new_fm_lines = []
                status_updated = False
                
                for line in fm_content.split("\n"):
                    if line.strip().startswith("status:"):
                        new_fm_lines.append(f"status: {new_status}")
                        status_updated = True
                    else:
                        new_fm_lines.append(line)
                
                if status_updated:
                    new_content = f"---\n{'\n'.join(new_fm_lines)}\n---{parts[2]}"
                    
                    if not dry_run:
                        filepath.write_text(new_content, encoding='utf-8')
                        log_action(f"Updated status to '{new_status}' in {filepath.name}")
                    else:
                        print(f"[DRY-RUN] Would update status to '{new_status}' in {filepath.name}")
                    return True
        
        return False
        
    except Exception as e:
        log_error(f"Failed to update status in '{filepath.name}': {e}")
        return False


# =============================================================================
# APPROVAL CHECKER CLASS
# =============================================================================

class ApprovalChecker:
    """
    Human Approval Checker - Monitors and processes approval requests.
    
    Usage:
        checker = ApprovalChecker(timeout_seconds=7200)
        checker.check_all()
        
        # Or check specific file
        checker.check_file("example.md")
    """
    
    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS, dry_run: bool = False):
        self.timeout_seconds = timeout_seconds
        self.dry_run = dry_run
        self.processed_approvals: Set[str] = set()
        self.stats = {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "timed_out": 0,
            "errors": 0
        }
        
    def load_tracker(self) -> None:
        """Load processed approvals tracker"""
        self.processed_approvals = load_processed_approvals()
        
    def check_all(self) -> Dict[str, int]:
        """
        Check all pending approvals in Needs_Action folder.
        
        Returns:
            dict: Statistics about approval checks
        """
        self.load_tracker()
        
        if not NEEDS_ACTION_DIR.exists():
            print(f"[INFO] Needs_Action folder does not exist: {NEEDS_ACTION_DIR}")
            log_action("Needs_Action folder does not exist")
            return self.stats
        
        # Get all files in Needs_Action
        all_files = [f for f in NEEDS_ACTION_DIR.iterdir() if f.is_file()]
        
        # Filter for pending approval files
        pending_files = [f for f in all_files if is_pending_approval(f)]
        
        if not pending_files:
            print("[INFO] No pending approval files found")
            log_action("No pending approval files found")
            return self.stats
        
        print(f"Found {len(pending_files)} pending approval file(s)")
        log_action(f"Found {len(pending_files)} pending approval file(s) to check")
        
        for filepath in pending_files:
            self.check_file(filepath)
        
        return self.stats
    
    def check_file(self, filepath: Path) -> bool:
        """
        Check a single file for approval status.
        
        Args:
            filepath: Path to file to check
            
        Returns:
            bool: True if processed (approved/rejected/timeout), False if still pending
        """
        if not filepath.exists():
            return False
        
        filename = filepath.name
        
        # Skip already processed
        if filename in self.processed_approvals:
            print(f"[SKIP] Already processed: {filename}")
            return False
        
        print(f"\n[CHECK] {filename}")
        
        try:
            # Read file content
            content = filepath.read_text(encoding='utf-8')
            
            # Check for human decision
            status, reviewer = check_approval_status(content)
            
            if status == 'approved':
                # Human approved!
                self.stats['approved'] += 1
                reviewer_info = f" (by {reviewer})" if reviewer else ""
                print(f"[APPROVED] {filename}{reviewer_info}")
                log_action(f"Detected approval for {filename}{reviewer_info}")
                
                # Rename file
                if rename_file_with_status(filepath, 'approved', self.dry_run):
                    self._mark_processed(filename)
                return True
                
            elif status == 'rejected':
                # Human rejected!
                self.stats['rejected'] += 1
                reviewer_info = f" (by {reviewer})" if reviewer else ""
                print(f"[REJECTED] {filename}{reviewer_info}")
                log_action(f"Detected rejection for {filename}{reviewer_info}")
                
                # Rename file
                if rename_file_with_status(filepath, 'rejected', self.dry_run):
                    self._mark_processed(filename)
                return True
                
            else:
                # Still pending - check for timeout
                self.stats['pending'] += 1
                return self._check_timeout(filepath)
                
        except Exception as e:
            log_error(f"Error checking '{filename}': {e}")
            self.stats['errors'] += 1
            print(f"[ERROR] {filename}: {e}")
            return False
    
    def _check_timeout(self, filepath: Path) -> bool:
        """
        Check if file has timed out.
        
        Args:
            filepath: Path to file to check
            
        Returns:
            bool: True if timed out, False if still within timeout
        """
        try:
            # Get file creation/modification time
            file_time = get_file_creation_time(filepath)
            elapsed = datetime.now() - file_time
            elapsed_seconds = elapsed.total_seconds()
            
            if elapsed_seconds >= self.timeout_seconds:
                # Timeout elapsed!
                self.stats['timed_out'] += 1
                self.stats['pending'] -= 1  # Remove from pending count
                
                timeout_hours = elapsed_seconds / 3600
                print(f"[TIMEOUT] {filepath.name} ({timeout_hours:.1f} hours elapsed)")
                log_action(f"Timeout for {filepath.name} ({timeout_hours:.1f} hours elapsed)")
                
                # Rename file
                if rename_file_with_status(filepath, 'timeout', self.dry_run):
                    self._mark_processed(filepath.name)
                return True
            else:
                # Still within timeout
                remaining_minutes = (self.timeout_seconds - elapsed_seconds) / 60
                print(f"[PENDING] {filepath.name} ({remaining_minutes:.0f} min remaining)")
                return False
                
        except Exception as e:
            log_error(f"Error checking timeout for '{filepath.name}': {e}")
            self.stats['errors'] += 1
            return False
    
    def _mark_processed(self, filename: str) -> None:
        """Mark a file as processed"""
        if not self.dry_run:
            save_processed_approval(filename)
            self.processed_approvals.add(filename)
    
    def print_summary(self) -> None:
        """Print approval check summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║              ✅ Human Approval Check Complete             ║
╠══════════════════════════════════════════════════════════╣
║  Pending approvals: {self.stats['pending']:<35} ║
║  Approved: {self.stats['approved']:<43} ║
║  Rejected: {self.stats['rejected']:<43} ║
║  Timed out: {self.stats['timed_out']:<42} ║
║  Errors: {self.stats['errors']:<46} ║
╚══════════════════════════════════════════════════════════╝
"""
        print(summary)


# =============================================================================
# WATCH MODE
# =============================================================================

def run_watch_mode(timeout_seconds: int, interval: int, dry_run: bool = False):
    """
    Run approval checker in continuous watch mode.
    
    Args:
        timeout_seconds: Timeout duration in seconds
        interval: Check interval in seconds
        dry_run: If True, don't make changes
    """
    checker = ApprovalChecker(timeout_seconds=timeout_seconds, dry_run=dry_run)
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              👁️ Approval Watch Mode                       ║
╠══════════════════════════════════════════════════════════╣
║  Timeout: {timeout_seconds / 3600:.1f} hours ({timeout_seconds} seconds){' ' * 28} ║
║  Check Interval: {interval} seconds{' ' * 36} ║
║  Dry Run: {dry_run}{' ' * 45} ║
╚══════════════════════════════════════════════════════════╝

Press Ctrl+C to stop watching
""")
    
    log_action(f"Approval watch mode started (timeout={timeout_seconds}s, interval={interval}s)")
    
    try:
        while True:
            checker.check_all()
            checker.print_summary()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nWatch mode stopped by user.")
        log_action("Approval watch mode stopped")


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Human Approval Checker - Monitor and process approval requests"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS}s = 2 hours)"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Check a specific file (default: check all)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview actions without making changes"
    )
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Run in continuous watch mode"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="Check interval in seconds for watch mode (default: 60)"
    )
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = ApprovalChecker(timeout_seconds=args.timeout, dry_run=args.dry_run)
    
    if args.dry_run:
        print("[DRY-RUN MODE] No changes will be made\n")
    
    if args.watch:
        # Continuous watch mode
        run_watch_mode(args.timeout, args.interval, args.dry_run)
    elif args.file:
        # Check specific file
        filepath = NEEDS_ACTION_DIR / args.file
        if filepath.exists():
            checker.check_file(filepath)
        else:
            print(f"[ERROR] File not found: {filepath}")
            sys.exit(1)
    else:
        # Check all files
        checker.check_all()
    
    # Print summary
    checker.print_summary()
    
    # Exit with error code if there were errors
    if checker.stats['errors'] > 0:
        sys.exit(1)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
