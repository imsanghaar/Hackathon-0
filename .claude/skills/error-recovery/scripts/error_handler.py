#!/usr/bin/env python3
"""
Error Handler Module

Core error handling and recovery logic for the AI Employee system.
Provides:
- Error logging with full details
- File quarantine to Errors folder
- Automatic retry queue management
- Error categorization and statistics

Usage:
    from error_handler import ErrorHandler
    
    handler = ErrorHandler()
    handler.handle_error(filename, error, source, retry=True)
"""

import os
import json
import shutil
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List


# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
BASE_DIR = SKILL_DIR.parent.parent

# File paths
LOGS_DIR = BASE_DIR / "Logs"
ERRORS_LOG = LOGS_DIR / "errors.log"
RETRY_QUEUE = LOGS_DIR / "retry_queue.json"
ERRORS_FOLDER = BASE_DIR / "AI_Employee_Vault" / "Errors"
INBOX_FOLDER = BASE_DIR / "AI_Employee_Vault" / "Inbox"
NEEDS_ACTION_FOLDER = BASE_DIR / "Needs_Action"

# Retry settings
RETRY_DELAY_MINUTES = 5
MAX_RETRY_ATTEMPTS = 2

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ERRORS_FOLDER.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ERROR CATEGORIZATION
# =============================================================================

class ErrorCategory:
    """Error category constants"""
    NETWORK = "network"
    FILE = "file"
    PERMISSION = "permission"
    PARSING = "parsing"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


def categorize_error(error: Exception) -> str:
    """
    Categorize an error for appropriate handling.
    
    Args:
        error: The exception to categorize
        
    Returns:
        str: Error category
    """
    error_type = type(error).__name__
    error_str = str(error).lower()
    
    # Network errors
    network_keywords = ["connection", "timeout", "network", "socket", "http", "request", "urllib", "aiohttp"]
    if any(kw in error_str for kw in network_keywords):
        return ErrorCategory.NETWORK
    if error_type in ["ConnectionError", "TimeoutError", "ConnectionRefusedError", "ConnectionResetError"]:
        return ErrorCategory.NETWORK
    
    # File errors
    file_keywords = ["file", "path", "directory", "folder", "not found", "no such file"]
    if any(kw in error_str for kw in file_keywords):
        return ErrorCategory.FILE
    if error_type in ["FileNotFoundError", "IsADirectoryError", "NotADirectoryError"]:
        return ErrorCategory.FILE
    
    # Permission errors
    permission_keywords = ["permission", "denied", "unauthorized", "access", "forbidden"]
    if any(kw in error_str for kw in permission_keywords):
        return ErrorCategory.PERMISSION
    if error_type in ["PermissionError", "PermissionDenied"]:
        return ErrorCategory.PERMISSION
    
    # Parsing errors
    parsing_keywords = ["json", "parse", "yaml", "xml", "decode", "invalid", "syntax", "format"]
    if any(kw in error_str for kw in parsing_keywords):
        return ErrorCategory.PARSING
    if error_type in ["JSONDecodeError", "YAMLError", "ParserError", "SyntaxError"]:
        return ErrorCategory.PARSING
    
    # Validation errors
    validation_keywords = ["validation", "invalid", "required", "missing", "expected"]
    if any(kw in error_str for kw in validation_keywords):
        return ErrorCategory.VALIDATION
    if error_type in ["ValidationError", "ValueError", "TypeError"]:
        return ErrorCategory.VALIDATION
    
    return ErrorCategory.UNKNOWN


# =============================================================================
# ERROR HANDLER CLASS
# =============================================================================

class ErrorHandler:
    """
    Centralized error handling and recovery system.
    
    Features:
    - Detailed error logging
    - File quarantine
    - Automatic retry queue
    - Error statistics
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize error handler.
        
        Args:
            base_dir: Base directory for AI Employee system (optional)
        """
        if base_dir:
            self.base_dir = Path(base_dir)
            self.logs_dir = self.base_dir / "Logs"
            self.errors_folder = self.base_dir / "AI_Employee_Vault" / "Errors"
            self.inbox_folder = self.base_dir / "AI_Employee_Vault" / "Inbox"
        else:
            self.base_dir = BASE_DIR
            self.logs_dir = LOGS_DIR
            self.errors_folder = ERRORS_FOLDER
            self.inbox_folder = INBOX_FOLDER
        
        self.errors_log = self.logs_dir / "errors.log"
        self.retry_queue_file = self.logs_dir / "retry_queue.json"
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.errors_folder.mkdir(parents=True, exist_ok=True)
    
    def handle_error(
        self,
        filename: str,
        error: Exception,
        source: str,
        retry: bool = True,
        extra_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Handle an error: log it, move file, and optionally queue for retry.
        
        Args:
            filename: Name of the file that caused the error
            error: The exception that was raised
            source: The skill/module where the error occurred
            retry: Whether to queue for retry
            extra_info: Additional information to log
            
        Returns:
            dict: Status of error handling
        """
        timestamp = datetime.now()
        error_category = categorize_error(error)
        stack_trace = traceback.format_exc()
        
        # Log the error
        self.log_error(filename, error, source, error_category, stack_trace, extra_info)
        
        # Move file to Errors folder
        file_action = self.move_to_errors(filename)
        
        # Queue for retry if enabled
        retry_status = "not_queued"
        if retry and error_category in [ErrorCategory.NETWORK, ErrorCategory.FILE]:
            retry_status = self.queue_retry(filename, source, error_category, stack_trace)
        
        return {
            "status": "handled",
            "timestamp": timestamp.isoformat(),
            "filename": filename,
            "source": source,
            "category": error_category,
            "file_action": file_action,
            "retry_status": retry_status
        }
    
    def log_error(
        self,
        filename: str,
        error: Exception,
        source: str,
        category: str,
        stack_trace: str,
        extra_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Write error to log file.
        
        Args:
            filename: File that caused the error
            error: The exception
            source: Source module/skill
            category: Error category
            stack_trace: Full stack trace
            extra_info: Additional information
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_type = type(error).__name__
        error_message = str(error)
        
        log_entry = f"""[{timestamp}] [ERROR] [{source}] File: {filename}
  Type: {error_type}
  Category: {category}
  Message: {error_message}
  Action: Moved to Errors folder
"""
        
        if extra_info:
            log_entry += f"  Extra: {json.dumps(extra_info)}\n"
        
        log_entry += f"  Stack Trace:\n{stack_trace}\n"
        log_entry += "  " + "=" * 60 + "\n\n"
        
        try:
            with open(self.errors_log, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[ERROR] Failed to write error log: {e}")
    
    def move_to_errors(self, filename: str) -> str:
        """
        Move a failed file to the Errors folder.
        
        Args:
            filename: Name or path of the file to move
            
        Returns:
            str: Status of the move operation
        """
        try:
            # Try multiple possible source locations
            possible_paths = [
                Path(filename),  # Full path
                self.inbox_folder / filename,
                self.base_dir / "Needs_Action" / filename,
                self.base_dir / filename,
            ]
            
            source_path = None
            for path in possible_paths:
                if path.exists():
                    source_path = path
                    break
            
            if not source_path:
                return f"file_not_found: {filename}"
            
            # Create destination path with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_name = f"{timestamp}_{source_path.name}"
            dest_path = self.errors_folder / dest_name
            
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            return f"moved_to_errors: {dest_name}"
            
        except Exception as e:
            return f"move_failed: {str(e)}"
    
    def queue_retry(
        self,
        filename: str,
        source: str,
        category: str,
        stack_trace: str
    ) -> str:
        """
        Add a file to the retry queue.
        
        Args:
            filename: File to retry
            source: Source module/skill
            category: Error category
            stack_trace: Stack trace from original error
            
        Returns:
            str: Status of queue operation
        """
        try:
            # Load existing queue
            queue = self.load_retry_queue()
            
            # Check if already in queue
            for item in queue.get("pending_retries", []):
                if item.get("filename") == filename:
                    return "already_queued"
            
            # Add to queue
            retry_time = datetime.now() + timedelta(minutes=RETRY_DELAY_MINUTES)
            
            queue.setdefault("pending_retries", []).append({
                "filename": filename,
                "source": source,
                "category": category,
                "retry_time": retry_time.isoformat(),
                "attempts": 1,
                "max_attempts": MAX_RETRY_ATTEMPTS,
                "stack_trace": stack_trace,
                "created_at": datetime.now().isoformat()
            })
            
            # Save queue
            self.save_retry_queue(queue)
            
            return f"queued_for_retry_at: {retry_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
        except Exception as e:
            return f"queue_failed: {str(e)}"
    
    def load_retry_queue(self) -> Dict[str, Any]:
        """Load the retry queue from file."""
        try:
            if self.retry_queue_file.exists():
                with open(self.retry_queue_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"pending_retries": []}
    
    def save_retry_queue(self, queue: Dict[str, Any]) -> None:
        """Save the retry queue to file."""
        try:
            with open(self.retry_queue_file, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save retry queue: {e}")
    
    def process_retry_queue(self) -> Dict[str, Any]:
        """
        Process the retry queue and retry files that are due.
        
        Returns:
            dict: Statistics about retry processing
        """
        stats = {
            "total_pending": 0,
            "retried": 0,
            "success": 0,
            "failed": 0,
            "max_attempts_reached": 0
        }
        
        try:
            queue = self.load_retry_queue()
            pending = queue.get("pending_retries", [])
            stats["total_pending"] = len(pending)
            
            now = datetime.now()
            still_pending = []
            
            for item in pending:
                retry_time = datetime.fromisoformat(item["retry_time"])
                
                if now >= retry_time:
                    # Time to retry
                    stats["retried"] += 1
                    
                    # Check if max attempts reached
                    if item["attempts"] >= item["max_attempts"]:
                        stats["max_attempts_reached"] += 1
                        # Move to permanent errors
                        self.move_to_errors(item["filename"])
                        continue
                    
                    # Attempt retry - move back to inbox
                    result = self._attempt_retry(item)
                    
                    if result["success"]:
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1
                        # Increment attempts and requeue
                        item["attempts"] += 1
                        item["retry_time"] = (now + timedelta(minutes=RETRY_DELAY_MINUTES)).isoformat()
                        still_pending.append(item)
                else:
                    # Not yet due
                    still_pending.append(item)
            
            # Update queue
            queue["pending_retries"] = still_pending
            self.save_retry_queue(queue)
            
        except Exception as e:
            print(f"[ERROR] Failed to process retry queue: {e}")
        
        return stats
    
    def _attempt_retry(self, item: Dict[str, Any]) -> Dict[str, bool]:
        """
        Attempt to retry a file by moving it back to inbox.
        
        Args:
            item: Retry queue item
            
        Returns:
            dict: Success status
        """
        try:
            # Find file in Errors folder
            filename = item["filename"]
            error_files = list(self.errors_folder.glob(f"*{filename}"))
            
            if not error_files:
                print(f"[RETRY] File not found in Errors: {filename}")
                return {"success": False}
            
            # Move back to inbox
            source_path = error_files[0]
            dest_path = self.inbox_folder / filename
            
            shutil.move(str(source_path), str(dest_path))
            print(f"[RETRY] {filename} moved back to Inbox for retry")
            
            return {"success": True}
            
        except Exception as e:
            print(f"[RETRY] Failed to retry {filename}: {e}")
            return {"success": False}
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            dict: Error statistics
        """
        stats = {
            "total_errors": 0,
            "errors_today": 0,
            "errors_this_week": 0,
            "pending_retries": 0,
            "files_in_errors": 0,
            "by_category": {},
            "by_source": {}
        }
        
        try:
            # Count errors in log
            if self.errors_log.exists():
                with open(self.errors_log, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    stats["total_errors"] = lines.count("  " + "=" * 60 + "\n")
                    
                    # Count today's errors
                    today = datetime.now().strftime("%Y-%m-%d")
                    for line in lines:
                        if line.startswith(f"[{today}]"):
                            stats["errors_today"] += 1
            
            # Count pending retries
            queue = self.load_retry_queue()
            stats["pending_retries"] = len(queue.get("pending_retries", []))
            
            # Count files in Errors folder
            stats["files_in_errors"] = len(list(self.errors_folder.glob("*")))
            
        except Exception as e:
            print(f"[ERROR] Failed to get error stats: {e}")
        
        return stats
    
    def cleanup_old_errors(self, days: int = 7) -> Dict[str, int]:
        """
        Remove old errors from log and Errors folder.
        
        Args:
            days: Remove errors older than this many days
            
        Returns:
            dict: Cleanup statistics
        """
        stats = {
            "log_entries_removed": 0,
            "files_removed": 0
        }
        
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            # Clean up Errors folder
            for file_path in self.errors_folder.glob("*"):
                try:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff:
                        file_path.unlink()
                        stats["files_removed"] += 1
                except Exception:
                    pass
            
            # Note: Log cleanup is more complex, typically we rotate logs
            # This is a simplified version
            print(f"[CLEANUP] Removed {stats['files_removed']} old error files")
            
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
        
        return stats
    
    def recover_file(self, filename: str) -> Dict[str, str]:
        """
        Manually recover a file from Errors folder.
        
        Args:
            filename: Name of the file to recover
            
        Returns:
            dict: Recovery status
        """
        try:
            # Find file in Errors folder
            error_files = list(self.errors_folder.glob(f"*{filename}"))
            
            if not error_files:
                return {"status": "not_found", "message": f"File not found: {filename}"}
            
            # Move back to inbox
            source_path = error_files[0]
            dest_path = self.inbox_folder / filename
            
            shutil.move(str(source_path), str(dest_path))
            
            # Remove from retry queue if present
            queue = self.load_retry_queue()
            queue["pending_retries"] = [
                item for item in queue.get("pending_retries", [])
                if item.get("filename") != filename
            ]
            self.save_retry_queue(queue)
            
            return {
                "status": "recovered",
                "message": f"Moved {filename} back to Inbox"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


# =============================================================================
# MODULE FUNCTIONS (Convenience Functions)
# =============================================================================

# Global error handler instance
_default_handler: Optional[ErrorHandler] = None


def get_handler() -> ErrorHandler:
    """Get the default error handler instance."""
    global _default_handler
    if _default_handler is None:
        _default_handler = ErrorHandler()
    return _default_handler


def handle_error(
    filename: str,
    error: Exception,
    source: str,
    retry: bool = True
) -> Dict[str, str]:
    """
    Handle an error using the default handler.
    
    Args:
        filename: File that caused the error
        error: The exception
        source: Source module/skill
        retry: Whether to queue for retry
        
    Returns:
        dict: Status of error handling
    """
    return get_handler().handle_error(filename, error, source, retry)


def process_retry_queue() -> Dict[str, Any]:
    """Process the retry queue using the default handler."""
    return get_handler().process_retry_queue()


def get_error_stats() -> Dict[str, Any]:
    """Get error statistics using the default handler."""
    return get_handler().get_error_stats()
