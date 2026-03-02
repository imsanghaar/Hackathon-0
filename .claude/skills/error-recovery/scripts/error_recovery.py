#!/usr/bin/env python3
"""
Error Recovery CLI

Command-line interface for the error recovery system.
Provides manual control over error handling and retry operations.

Usage:
    python error_recovery.py --check       # Check and process retry queue
    python error_recovery.py --recover <file>  # Recover a specific file
    python error_recovery.py --log         # View error log
    python error_recovery.py --queue       # View retry queue
    python error_recovery.py --cleanup     # Clean up old errors
    python error_recovery.py --status      # Show error statistics
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# Add script directory to path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from error_handler import ErrorHandler, get_error_stats


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_check(args):
    """Check and process retry queue."""
    handler = ErrorHandler()
    
    print("=" * 60)
    print("         Error Recovery - Processing Retry Queue")
    print("=" * 60)
    
    stats = handler.process_retry_queue()
    
    print(f"\nResults:")
    print(f"  Total Pending: {stats['total_pending']}")
    print(f"  Retried: {stats['retried']}")
    print(f"  Successful: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Max Attempts Reached: {stats['max_attempts_reached']}")
    print("=" * 60)
    
    return 0


def cmd_recover(args):
    """Recover a specific file from Errors folder."""
    handler = ErrorHandler()
    
    print("=" * 60)
    print(f"         Recovering File: {args.filename}")
    print("=" * 60)
    
    result = handler.recover_file(args.filename)
    
    if result["status"] == "recovered":
        print(f"[OK] {result['message']}")
    elif result["status"] == "not_found":
        print(f"[WARNING] {result['message']}")
    else:
        print(f"[ERROR] {result['message']}")
    
    print("=" * 60)
    
    return 0 if result["status"] == "recovered" else 1


def cmd_log(args):
    """Display recent error log entries."""
    errors_log = Path("Logs/errors.log")
    
    print("=" * 60)
    print("         Error Log")
    print("=" * 60)
    
    if not errors_log.exists():
        print("\n[INFO] No error log found.")
        return 0
    
    try:
        with open(errors_log, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Show last N errors
        limit = args.limit if hasattr(args, 'limit') else 50
        recent_lines = lines[-limit:]
        
        if recent_lines:
            print("".join(recent_lines))
        else:
            print("\n[INFO] Error log is empty.")
            
    except Exception as e:
        print(f"[ERROR] Failed to read error log: {e}")
        return 1
    
    print("=" * 60)
    return 0


def cmd_queue(args):
    """Display retry queue."""
    handler = ErrorHandler()
    queue = handler.load_retry_queue()
    
    print("=" * 60)
    print("         Retry Queue")
    print("=" * 60)
    
    pending = queue.get("pending_retries", [])
    
    if not pending:
        print("\n[INFO] Retry queue is empty.")
        return 0
    
    print(f"\nPending Retries: {len(pending)}\n")
    
    for i, item in enumerate(pending, 1):
        retry_time = datetime.fromisoformat(item["retry_time"])
        created = datetime.fromisoformat(item["created_at"])
        
        print(f"{i}. {item['filename']}")
        print(f"   Source: {item['source']}")
        print(f"   Category: {item['category']}")
        print(f"   Attempts: {item['attempts']}/{item['max_attempts']}")
        print(f"   Retry At: {retry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    print("=" * 60)
    return 0


def cmd_cleanup(args):
    """Clean up old errors."""
    handler = ErrorHandler()
    days = args.days if hasattr(args, 'days') else 7
    
    print("=" * 60)
    print(f"         Cleaning Up Errors Older Than {days} Days")
    print("=" * 60)
    
    stats = handler.cleanup_old_errors(days)
    
    print(f"\nResults:")
    print(f"  Files Removed: {stats['files_removed']}")
    print("=" * 60)
    
    return 0


def cmd_status(args):
    """Show error statistics."""
    stats = get_error_stats()

    print("=" * 60)
    print("         Error Recovery Status")
    print("=" * 60)

    print(f"\nStatistics:")
    print(f"  Total Errors Logged: {stats.get('total_errors', 0)}")
    print(f"  Errors Today: {stats.get('errors_today', 0)}")
    print(f"  Pending Retries: {stats.get('pending_retries', 0)}")
    print(f"  Files in Errors Folder: {stats.get('files_in_errors', 0)}")

    print("\n" + "=" * 60)

    return 0


def cmd_clear(args):
    """Clear all errors and retry queue."""
    handler = ErrorHandler()
    
    print("=" * 60)
    print("         Clearing All Errors and Retry Queue")
    print("=" * 60)
    
    try:
        # Clear retry queue
        handler.save_retry_queue({"pending_retries": []})
        print("[OK] Retry queue cleared")
        
        # Clear error log (rotate)
        errors_log = Path("Logs/errors.log")
        if errors_log.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived = Path(f"Logs/errors_{timestamp}.log")
            errors_log.rename(archived)
            print(f"[OK] Error log archived to {archived.name}")
        
        # Clear Errors folder
        errors_folder = Path("AI_Employee_Vault/Errors")
        if errors_folder.exists():
            count = 0
            for file_path in errors_folder.glob("*"):
                file_path.unlink()
                count += 1
            print(f"[OK] Removed {count} files from Errors folder")
        
        print("\n[OK] All errors cleared")
        
    except Exception as e:
        print(f"[ERROR] Failed to clear errors: {e}")
        return 1
    
    print("=" * 60)
    return 0


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Error Recovery System - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python error_recovery.py --check              # Process retry queue
  python error_recovery.py --recover file.md    # Recover specific file
  python error_recovery.py --log                # View error log
  python error_recovery.py --log --limit 100    # View last 100 log lines
  python error_recovery.py --queue              # View retry queue
  python error_recovery.py --cleanup            # Clean old errors
  python error_recovery.py --cleanup --days 14  # Clean errors older than 14 days
  python error_recovery.py --status             # Show statistics
  python error_recovery.py --clear              # Clear all errors
        """
    )
    
    # Commands
    parser.add_argument('--check', action='store_true',
                        help='Check and process retry queue')
    parser.add_argument('--recover', type=str, metavar='FILE',
                        help='Recover a specific file from Errors folder')
    parser.add_argument('--log', action='store_true',
                        help='Display recent error log entries')
    parser.add_argument('--queue', action='store_true',
                        help='Display retry queue')
    parser.add_argument('--cleanup', action='store_true',
                        help='Clean up old errors')
    parser.add_argument('--status', action='store_true',
                        help='Show error statistics')
    parser.add_argument('--clear', action='store_true',
                        help='Clear all errors and retry queue')
    
    # Options
    parser.add_argument('--limit', type=int, default=50,
                        help='Number of log lines to show (default: 50)')
    parser.add_argument('--days', type=int, default=7,
                        help='Days for cleanup (default: 7)')
    
    args = parser.parse_args()
    
    # Execute command
    if args.check:
        return cmd_check(args)
    elif args.recover:
        return cmd_recover(args)
    elif args.log:
        return cmd_log(args)
    elif args.queue:
        return cmd_queue(args)
    elif args.cleanup:
        return cmd_cleanup(args)
    elif args.status:
        return cmd_status(args)
    elif args.clear:
        return cmd_clear(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
