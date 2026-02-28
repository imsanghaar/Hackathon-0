#!/usr/bin/env python3
"""
AI Employee Scheduler - Silver Tier

Run vault-watcher and task-planner in a loop with configurable interval.
Supports --daemon, --once, --status modes.
Logs to logs/ai_employee.log with 4MB rotation.
Prevents duplicate instances with lock files.

Usage:
    python scripts/run_ai_employee.py --daemon     # Run continuously
    python scripts/run_ai_employee.py --once       # Single execution
    python scripts/run_ai_employee.py --status     # Show status

Features:
- Configurable interval (default 6 minutes)
- Log rotation at 4MB
- Lock file for duplicate prevention
- Graceful shutdown handling
- Comprehensive logging
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Cross-platform lock file support
try:
    import fcntl  # Unix/Linux/Mac
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    # Windows fallback
    try:
        import msvcrt
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent
SKILL_DIR = BASE_DIR / ".claude" / "skills"

# Define folder paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# File paths
AI_EMPLOYEE_LOG_FILE = LOGS_DIR / "ai_employee.log"
LOCK_FILE = LOGS_DIR / "scheduler.lock"
WATCHER_TRACKER = LOGS_DIR / "processed_files.txt"
PLANNER_TRACKER = LOGS_DIR / "planner_processed.txt"
APPROVAL_TRACKER = LOGS_DIR / "approval_tracker.txt"

# Default settings
DEFAULT_INTERVAL_SECONDS = 360  # 6 minutes
DEFAULT_MAX_LOG_SIZE = 4 * 1024 * 1024  # 4 MB


# =============================================================================
# LOGGING WITH ROTATION
# =============================================================================

def ensure_folders() -> None:
    """Ensure all required folders exist"""
    for folder in [INBOX_DIR, NEEDS_ACTION_DIR, DONE_DIR, LOGS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def get_log_size() -> int:
    """Get current log file size in bytes"""
    try:
        if AI_EMPLOYEE_LOG_FILE.exists():
            return AI_EMPLOYEE_LOG_FILE.stat().st_size
    except Exception:
        pass
    return 0


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def rotate_log_file() -> bool:
    """
    Rotate log file if it exceeds max size.
    
    Returns:
        bool: True if rotated, False otherwise
    """
    try:
        current_size = get_log_size()
        if current_size < DEFAULT_MAX_LOG_SIZE:
            return False
        
        # Generate timestamp for archived log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_name = f"ai_employee_{timestamp}.log"
        archived_path = LOGS_DIR / archived_name
        
        # Move current log to archived
        AI_EMPLOYEE_LOG_FILE.rename(archived_path)
        
        # Create fresh log file with header
        write_log(f"Log rotated - Previous log archived to {archived_name}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to rotate log: {e}", file=sys.stderr)
        return False


def write_log(message: str) -> None:
    """Write a message to the AI employee log file"""
    try:
        ensure_folders()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Check if rotation needed before writing
        rotate_log_file()
        
        with open(AI_EMPLOYEE_LOG_FILE, "a") as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"[ERROR] Failed to write log: {e}", file=sys.stderr)


def log_error(message: str) -> None:
    """Log an error message"""
    write_log(f"ERROR: {message}")


# =============================================================================
# LOCK FILE MANAGEMENT
# =============================================================================

class LockFile:
    """
    Lock file manager for preventing duplicate instances.
    
    Usage:
        with LockFile() as lock:
            if lock.acquired:
                # Do work
            else:
                # Another instance is running
    """
    
    def __init__(self, lock_path: Path):
        self.lock_path = lock_path
        self.lock_file = None
        self.acquired = False
        self.pid = os.getpid()
        
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        
    def acquire(self, force: bool = False) -> bool:
        """
        Acquire the lock file.
        
        Args:
            force: If True, override existing lock
            
        Returns:
            bool: True if lock acquired, False otherwise
        """
        try:
            ensure_folders()
            
            # Check for existing lock
            if self.lock_path.exists() and not force:
                try:
                    with open(self.lock_path, "r") as f:
                        old_pid = int(f.read().strip())
                    
                    # Check if old process is still running
                    if self._is_process_running(old_pid):
                        write_log(f"Scheduler already running (PID: {old_pid})")
                        print(f"[INFO] Scheduler already running (PID: {old_pid})")
                        print("Use --force to override")
                        return False
                    else:
                        # Stale lock - remove it
                        write_log(f"Removing stale lock (PID: {old_pid})")
                        self.lock_path.unlink()
                        
                except (ValueError, FileNotFoundError):
                    # Invalid lock file - remove it
                    self.lock_path.unlink()
            
            # Create new lock file
            self.lock_file = open(self.lock_path, "w")
            
            # Platform-specific file locking
            if HAS_FCNTL:
                # Unix/Linux/Mac
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif HAS_MSVCRT:
                # Windows
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                except IOError:
                    self.lock_file.close()
                    write_log("Failed to acquire Windows file lock")
                    return False
            
            self.lock_file.write(str(self.pid))
            self.lock_file.flush()
            self.acquired = True
            
            write_log(f"Scheduler lock acquired (PID: {self.pid})")
            return True
            
        except (IOError, OSError) as e:
            write_log(f"Failed to acquire lock: {e}")
            return False
    
    def release(self) -> None:
        """Release the lock file"""
        try:
            if self.lock_file:
                # Platform-specific file unlocking
                if HAS_FCNTL:
                    # Unix/Linux/Mac
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                elif HAS_MSVCRT:
                    # Windows - unlock by seeking and locking 0 bytes
                    self.lock_file.seek(0)
                    try:
                        msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    except IOError:
                        pass  # Ignore unlock errors on Windows
                
                self.lock_file.close()

            if self.lock_path.exists():
                self.lock_path.unlink()

            write_log(f"Scheduler lock released (PID: {self.pid})")
            self.acquired = False

        except Exception as e:
            log_error(f"Failed to release lock: {e}")
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


# =============================================================================
# VAULT WATCHER INTEGRATION
# =============================================================================

def run_vault_watcher() -> Dict[str, Any]:
    """
    Run vault-watcher cycle.
    
    Returns:
        dict: Statistics from watcher cycle
    """
    try:
        write_log("Running vault-watcher cycle")
        
        # Import and run watcher
        sys.path.insert(0, str(SCRIPT_DIR))
        from watch_inbox import (
            ensure_folders, load_processed_files, get_inbox_md_files,
            process_new_file, log_action
        )
        
        # Load processed files
        processed_files = load_processed_files()
        
        # Get inbox files
        inbox_files = get_inbox_md_files()
        new_files = inbox_files - processed_files
        
        stats = {
            "inbox_count": len(inbox_files),
            "new_files": len(new_files),
            "processed": 0,
            "errors": 0
        }
        
        # Process new files
        for filename in new_files:
            try:
                # Create task file for new inbox file (simplified watcher logic)
                from watch_inbox import create_task_file, save_processed_file
                
                create_task_file(filename)
                save_processed_file(filename, processed_files)
                stats["processed"] += 1
                
            except Exception as e:
                log_error(f"Watcher error processing '{filename}': {e}")
                stats["errors"] += 1
        
        write_log(f"Vault-watcher: {stats['new_files']} new files, {stats['processed']} processed")
        return stats
        
    except Exception as e:
        log_error(f"Vault-watcher cycle failed: {e}")
        return {"inbox_count": 0, "new_files": 0, "processed": 0, "errors": 1}


# =============================================================================
# TASK PLANNER INTEGRATION
# =============================================================================

def run_task_planner() -> Dict[str, Any]:
    """
    Run task-planner cycle.

    Returns:
        dict: Statistics from planner cycle
    """
    try:
        write_log("Running task-planner cycle")

        # Import and run planner
        sys.path.insert(0, str(SCRIPT_DIR))
        from task_planner import TaskPlanner

        # Run planner (dry_run=False to actually process)
        planner = TaskPlanner(dry_run=False)
        stats = planner.process_inbox()

        write_log(f"Task-planner: {stats['files_processed']} files, {stats['plans_created']} plans")
        return stats

    except Exception as e:
        log_error(f"Task-planner cycle failed: {e}")
        return {"files_processed": 0, "plans_created": 0, "files_moved": 0, "errors": 1}


# =============================================================================
# GMAIL WATCHER INTEGRATION
# =============================================================================

def run_gmail_watcher() -> Dict[str, Any]:
    """
    Run gmail-watcher cycle to check for new emails.

    Returns:
        dict: Statistics from gmail-watcher cycle
    """
    try:
        write_log("Running gmail-watcher cycle")

        # Import and run gmail watcher
        gmail_watcher_script = SKILL_DIR / "gmail-watcher" / "scripts" / "watch_gmail.py"
        
        if not gmail_watcher_script.exists():
            write_log("Gmail-watcher script not found")
            return {"emails_checked": 0, "tasks_created": 0, "errors": 0}

        # Run gmail watcher as subprocess (non-interactive)
        result = subprocess.run(
            [sys.executable, str(gmail_watcher_script)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(gmail_watcher_script.parent)
        )

        # Parse output for stats
        emails_checked = 0
        tasks_created = 0
        
        for line in result.stdout.split('\n'):
            if 'Checked' in line and 'emails' in line:
                try:
                    emails_checked = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            if 'Created' in line and 'tasks' in line:
                try:
                    tasks_created = int(line.split(':')[1].strip().split()[0])
                except:
                    pass

        if result.returncode != 0 and result.stderr:
            write_log(f"Gmail-watcher error: {result.stderr}")

        write_log(f"Gmail-watcher: {emails_checked} emails checked, {tasks_created} tasks created")
        return {"emails_checked": emails_checked, "tasks_created": tasks_created, "errors": 0}

    except subprocess.TimeoutExpired:
        log_error("Gmail-watcher timeout (60s)")
        return {"emails_checked": 0, "tasks_created": 0, "errors": 1}
    except Exception as e:
        log_error(f"Gmail-watcher cycle failed: {e}")
        return {"emails_checked": 0, "tasks_created": 0, "errors": 1}


# =============================================================================
# STATUS DISPLAY
# =============================================================================

def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status"""
    status = {
        "running": False,
        "pid": None,
        "inbox_count": 0,
        "pending_tasks": 0,
        "last_cycle": "Never",
        "log_size": "0 B"
    }
    
    # Check if scheduler is running
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            if os.path.exists(f"/proc/{pid}"):
                status["running"] = True
                status["pid"] = pid
        except (ValueError, FileNotFoundError):
            pass
    
    # Count inbox files
    if INBOX_DIR.exists():
        status["inbox_count"] = len([f for f in INBOX_DIR.iterdir() if f.is_file()])
    
    # Count pending tasks
    if NEEDS_ACTION_DIR.exists():
        status["pending_tasks"] = len([f for f in NEEDS_ACTION_DIR.iterdir() if f.is_file()])
    
    # Get log size
    status["log_size"] = format_size(get_log_size())
    
    # Get last cycle from log
    if AI_EMPLOYEE_LOG_FILE.exists():
        try:
            with open(AI_EMPLOYEE_LOG_FILE, "r") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if "Cycle complete" in line:
                        # Extract timestamp
                        if line.startswith("["):
                            end_idx = line.find("]")
                            if end_idx > 0:
                                status["last_cycle"] = line[1:end_idx]
                        break
        except Exception:
            pass
    
    return status


def print_status():
    """Print scheduler status"""
    status = get_scheduler_status()

    running_str = f"Running (PID: {status['pid']})" if status["running"] else "Not running"

    banner = f"""
+==========================================================+
|           AI Employee Scheduler Status                   |
+==========================================================+
|  Scheduler Status: {running_str:<34} |
|  Inbox Files: {status['inbox_count']:<41} |
|  Pending Tasks: {status['pending_tasks']:<39} |
|  Last Cycle: {status['last_cycle']:<42} |
|  Log Size: {status['log_size']:<44} |
+==========================================================+
"""
    print(banner)


# =============================================================================
# SCHEDULER MAIN LOOP
# =============================================================================

class Scheduler:
    """
    Main scheduler class for running vault-watcher and task-planner cycles.
    """
    
    def __init__(self, interval: int = DEFAULT_INTERVAL_SECONDS):
        self.interval = interval
        self.running = False
        self.cycle_count = 0
        
    def run_cycle(self) -> None:
        """Run a single scheduler cycle"""
        self.cycle_count += 1
        write_log(f"Starting scheduler cycle #{self.cycle_count}")

        print(f"\n[CYCLE {self.cycle_count}] Running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # [1/3] Run vault-watcher
        print("[1/3] Running vault-watcher...")
        watcher_stats = run_vault_watcher()
        print(f"      Inbox: {watcher_stats['inbox_count']} files, {watcher_stats['new_files']} new")

        # [2/3] Run gmail-watcher (check for new emails)
        print("[2/3] Running gmail-watcher...")
        gmail_stats = run_gmail_watcher()
        print(f"      Gmail: {gmail_stats['emails_checked']} checked, {gmail_stats['tasks_created']} new tasks")

        # [3/3] Run task-planner
        print("[3/3] Running task-planner...")
        planner_stats = run_task_planner()
        print(f"      Processed: {planner_stats['files_processed']}, Plans: {planner_stats['plans_created']}")

        write_log(f"Cycle complete - Inbox: {watcher_stats['inbox_count']}, Gmail: {gmail_stats['emails_checked']}, Processed: {planner_stats['files_processed']}")
        print(f"[CYCLE {self.cycle_count}] Complete")
    
    def run_daemon(self) -> None:
        """Run scheduler in daemon mode (continuous)"""
        self.running = True

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print(f"""
+==========================================================+
|           AI Employee Scheduler - Silver Tier            |
+==========================================================+
|  Mode: Daemon (continuous)                               |
|  Interval: {self.interval / 60:.1f} minutes ({self.interval} seconds){' ' * 25} |
|  Log File: logs/ai_employee.log                          |
|  Max Log Size: 4 MB                                      |
+==========================================================+

Press Ctrl+C to stop
""")
        
        write_log(f"Scheduler started in daemon mode (interval={self.interval}s)")
        
        try:
            while self.running:
                self.run_cycle()
                
                # Wait for next cycle
                next_run = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[Zzz] Next cycle in {self.interval} seconds...")
                write_log(f"Next cycle in {self.interval} seconds")
                
                # Sleep in small intervals to respond to signals quickly
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            log_error(f"Daemon error: {e}")
        finally:
            write_log(f"Scheduler stopped after {self.cycle_count} cycles")
            print("\nScheduler stopped.")
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals"""
        write_log(f"Received signal {signum}, shutting down...")
        self.running = False


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def print_banner():
    """Print startup banner"""
    print(f"""
+==========================================================+
|           AI Employee Scheduler - Silver Tier            |
|                    By ISC                                |
+==========================================================+
""")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Employee Scheduler - Silver Tier"
    )
    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run in daemon mode (continuous)"
    )
    parser.add_argument(
        "--once", "-o",
        action="store_true",
        help="Run single cycle and exit"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show scheduler status"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Interval in seconds for daemon mode (default: {DEFAULT_INTERVAL_SECONDS}s)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force start (ignore existing lock)"
    )
    
    args = parser.parse_args()
    
    # Ensure folders exist
    ensure_folders()
    
    # Handle status mode (no lock needed)
    if args.status:
        print_status()
        return 0
    
    # Require either --daemon, --once, or --status
    if not (args.daemon or args.once):
        parser.print_help()
        print("\n[ERROR] Must specify --daemon, --once, or --status")
        return 1
    
    # Acquire lock (unless --force)
    lock = LockFile(LOCK_FILE)
    if not lock.acquire(force=args.force):
        return 1
    
    try:
        print_banner()
        
        if args.daemon:
            # Daemon mode
            scheduler = Scheduler(interval=args.interval)
            scheduler.run_daemon()
        else:
            # Once mode
            write_log("Scheduler started in once mode")
            print(f"""
+==========================================================+
|           AI Employee Scheduler - Silver Tier            |
+==========================================================+
|  Mode: Once (single execution)                           |
|  Log File: logs/ai_employee.log                          |
+==========================================================+
""")
            scheduler = Scheduler()
            scheduler.run_cycle()
            write_log("Scheduler completed once mode")
            print("\n[DONE] Single cycle complete")
        
        return 0
        
    except Exception as e:
        log_error(f"Scheduler failed: {e}")
        print(f"\n[ERROR] {e}", file=sys.stderr)
        return 1
        
    finally:
        lock.release()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    sys.exit(main())
