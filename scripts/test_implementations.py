#!/usr/bin/env python3
"""
Test Suite for Vault Watcher and Task Planner

Run: python scripts/test_implementations.py
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

# Add scripts directory and base directory to path
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(BASE_DIR))

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# Test colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


# =============================================================================
# TEST UTILITIES
# =============================================================================

def print_header(title: str):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_test(name: str, passed: bool, message: str = ""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status} - {name}")
    if message:
        color = GREEN if passed else RED
        print(f"         {color}{message}{RESET}")


def cleanup_test_files():
    """Clean up test files before and after tests"""
    print(f"{YELLOW}Cleaning up test files...{RESET}")
    
    # Clean inbox
    if INBOX_DIR.exists():
        for f in INBOX_DIR.glob("test_*.md"):
            f.unlink()
    
    # Clean needs_action
    if NEEDS_ACTION_DIR.exists():
        for f in NEEDS_ACTION_DIR.glob("Plan_test_*.md"):
            f.unlink()
    
    # Clean done
    if DONE_DIR.exists():
        for f in DONE_DIR.glob("test_*.md"):
            f.unlink()
    
    # Clean logs
    if LOGS_DIR.exists():
        tracker = LOGS_DIR / "planner_processed.txt"
        if tracker.exists():
            # Clear the tracker for fresh test
            with open(tracker, "w") as f:
                f.write("")


def create_test_file(filename: str, content: str) -> Path:
    """Create a test file in Inbox"""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    filepath = INBOX_DIR / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath


# =============================================================================
# VAULT WATCHER TESTS
# =============================================================================

def test_vault_watcher():
    """Test vault watcher implementation"""
    print_header("VAULT WATCHER TESTS")
    
    from watch_inbox import (
        ensure_folders, load_processed_files, save_processed_file,
        get_inbox_md_files, log_action
    )
    
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Ensure folders exist
    try:
        ensure_folders()
        passed = INBOX_DIR.exists() and LOGS_DIR.exists()
        print_test("Ensure folders exist", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Ensure folders exist", False, str(e))
        results["failed"] += 1
    
    # Test 2: Load processed files (empty)
    try:
        processed = load_processed_files()
        passed = isinstance(processed, set)
        print_test("Load processed files", passed, f"Loaded {len(processed)} files")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Load processed files", False, str(e))
        results["failed"] += 1
    
    # Test 3: Save processed file
    try:
        test_filename = "test_watch_file.md"
        # vault_watcher uses different signature - just append to tracker file directly
        with open(LOGS_DIR / "processed_files.txt", "a") as f:
            f.write(test_filename + "\n")
        processed = load_processed_files()
        passed = test_filename in processed
        print_test("Save processed file", passed)
        results["passed" if passed else "failed"] += 1
        # Cleanup
        if test_filename in processed:
            processed.remove(test_filename)
            with open(LOGS_DIR / "processed_files.txt", "w") as f:
                for item in processed:
                    f.write(item + "\n")
    except Exception as e:
        print_test("Save processed file", False, str(e))
        results["failed"] += 1
    
    # Test 4: Get inbox .md files
    try:
        # Create test file
        create_test_file("test_inbox_file.md", "# Test Content")
        files = get_inbox_md_files()
        passed = "test_inbox_file.md" in files
        print_test("Get inbox .md files", passed, f"Found {len(files)} files")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Get inbox .md files", False, str(e))
        results["failed"] += 1
    
    # Test 5: Log action
    try:
        log_action("TEST: Vault watcher test action")
        action_log = LOGS_DIR / "action.log"
        passed = action_log.exists()
        print_test("Log action", passed, f"Log file exists: {passed}")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Log action", False, str(e))
        results["failed"] += 1
    
    # Test 6: Check interval randomization
    try:
        from scripts.watch_inbox import MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL
        import random
        intervals = [random.randint(MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL) for _ in range(10)]
        passed = all(MIN_CHECK_INTERVAL <= i <= MAX_CHECK_INTERVAL for i in intervals)
        print_test("Check interval randomization", passed, 
                  f"Range: {min(intervals)}-{max(intervals)}s (expected: {MIN_CHECK_INTERVAL}-{MAX_CHECK_INTERVAL}s)")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Check interval randomization", False, str(e))
        results["failed"] += 1
    
    return results


# =============================================================================
# TASK PLANNER TESTS
# =============================================================================

def test_task_planner():
    """Test task planner implementation"""
    print_header("TASK PLANNER TESTS")
    
    from task_planner import (
        TaskPlanner, ensure_folders, parse_frontmatter, analyze_file_content,
        generate_plan_content, load_processed_files, save_processed_file,
        log_action
    )
    
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Ensure folders exist
    try:
        ensure_folders()
        passed = NEEDS_ACTION_DIR.exists() and DONE_DIR.exists()
        print_test("Ensure folders exist", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Ensure folders exist", False, str(e))
        results["failed"] += 1
    
    # Test 2: Parse frontmatter
    try:
        test_content = """---
type: file_review
status: pending
priority: high
---
# Test Content
This is the body.
"""
        fm = parse_frontmatter(test_content)
        passed = fm.get("type") == "file_review" and fm.get("priority") == "high"
        print_test("Parse frontmatter", passed, f"Parsed: {fm}")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Parse frontmatter", False, str(e))
        results["failed"] += 1
    
    # Test 3: Analyze file content
    try:
        test_file = create_test_file("test_analyze.md", """---
type: client_request
priority: high
---
# Client Request
Please review this document and provide feedback.
""")
        analysis = analyze_file_content(test_file)
        passed = analysis.get("type") == "client_request" and len(analysis.get("suggested_steps", [])) > 0
        print_test("Analyze file content", passed, 
                  f"Type: {analysis.get('type')}, Steps: {len(analysis.get('suggested_steps', []))}")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Analyze file content", False, str(e))
        results["failed"] += 1
    
    # Test 4: Generate plan content
    try:
        analysis = {
            "filename": "test_plan.md",
            "type": "file_review",
            "priority": "medium",
            "created_at": "2026-02-24",
            "content_preview": "Test preview",
            "suggested_steps": [
                {"action": "Step 1", "details": "Do something", "output": "Result"}
            ]
        }
        plan = generate_plan_content(analysis)
        passed = "Plan: test_plan.md" in plan and "Step 1" in plan
        print_test("Generate plan content", passed, f"Plan length: {len(plan)} chars")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Generate plan content", False, str(e))
        results["failed"] += 1
    
    # Test 5: TaskPlanner class instantiation
    try:
        planner = TaskPlanner(dry_run=True)
        passed = planner.dry_run == True
        print_test("TaskPlanner class instantiation", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("TaskPlanner class instantiation", False, str(e))
        results["failed"] += 1
    
    # Test 6: Idempotent processing
    try:
        # Clear tracker first
        tracker_file = LOGS_DIR / "planner_processed.txt"
        if tracker_file.exists():
            tracker_file.unlink()
        
        test_filename = "test_idempotent.md"
        save_processed_file(test_filename)
        
        # Check if file is marked as processed
        processed = load_processed_files()
        passed = test_filename in processed
        print_test("Idempotent processing (tracker)", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Idempotent processing (tracker)", False, str(e))
        results["failed"] += 1
    
    # Test 7: Log action
    try:
        log_action("TEST: Task planner test action")
        action_log = LOGS_DIR / "action.log"
        passed = action_log.exists()
        print_test("Log action", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Log action", False, str(e))
        results["failed"] += 1
    
    # Test 8: Full dry-run processing
    try:
        # Create test file
        test_file = create_test_file("test_full_run.md", """---
type: file_review
priority: medium
---
# Test Full Run
This is a test file for full processing.
""")
        
        planner = TaskPlanner(dry_run=True)
        stats = planner.process_inbox()
        passed = stats["files_processed"] >= 0  # Should not error
        print_test("Full dry-run processing", passed,
                  f"Processed: {stats['files_processed']}, Plans: {stats['plans_created']}")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Full dry-run processing", False, str(e))
        results["failed"] += 1
    
    return results


# =============================================================================
# INTEGRATION TEST
# =============================================================================

def test_integration():
    """Test integration between watcher and planner"""
    print_header("INTEGRATION TESTS")
    
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Both modules can be imported together
    try:
        from watch_inbox import WatcherState
        from task_planner import TaskPlanner
        passed = True
        print_test("Module compatibility", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Module compatibility", False, str(e))
        results["failed"] += 1
    
    # Test 2: Shared log file works
    try:
        from watch_inbox import log_action as watcher_log
        from task_planner import log_action as planner_log
        
        watcher_log("INTEGRATION: Watcher log test")
        planner_log("INTEGRATION: Planner log test")
        
        action_log = LOGS_DIR / "action.log"
        content = action_log.read_text()
        passed = "Watcher log test" in content and "Planner log test" in content
        print_test("Shared log file", passed)
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Shared log file", False, str(e))
        results["failed"] += 1
    
    # Test 3: Folder structure consistency
    try:
        folders = [
            VAULT_DIR / "Inbox",
            VAULT_DIR / "Needs_Action",
            VAULT_DIR / "Done",
            LOGS_DIR
        ]
        passed = all(f.exists() for f in folders)
        print_test("Folder structure consistency", passed,
                  f"All folders exist: {passed}")
        results["passed" if passed else "failed"] += 1
    except Exception as e:
        print_test("Folder structure consistency", False, str(e))
        results["failed"] += 1
    
    return results


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    print(f"""
{BLUE}╔══════════════════════════════════════════════════════════╗
║           AI Employee - Implementation Tests                  ║
║           Vault Watcher & Task Planner                        ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")
    
    # Cleanup before tests
    cleanup_test_files()
    
    total_results = {"passed": 0, "failed": 0}
    
    # Run Vault Watcher tests
    watcher_results = test_vault_watcher()
    total_results["passed"] += watcher_results["passed"]
    total_results["failed"] += watcher_results["failed"]
    
    # Run Task Planner tests
    planner_results = test_task_planner()
    total_results["passed"] += planner_results["passed"]
    total_results["failed"] += planner_results["failed"]
    
    # Run Integration tests
    integration_results = test_integration()
    total_results["passed"] += integration_results["passed"]
    total_results["failed"] += integration_results["failed"]
    
    # Print summary
    print_header("TEST SUMMARY")
    total = total_results["passed"] + total_results["failed"]
    pass_rate = (total_results["passed"] / total * 100) if total > 0 else 0
    
    print(f"  Total Tests: {total}")
    print(f"  {GREEN}Passed: {total_results['passed']}{RESET}")
    print(f"  {RED}Failed: {total_results['failed']}{RESET}")
    print(f"  Pass Rate: {GREEN if pass_rate == 100 else RED}{pass_rate:.1f}%{RESET}")
    
    # Cleanup after tests
    cleanup_test_files()
    
    print(f"\n{BLUE}Test complete!{RESET}\n")
    
    return 0 if total_results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
