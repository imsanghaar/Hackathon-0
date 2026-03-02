#!/usr/bin/env python3
"""
Task Planner - Production Ready

Reads new .md files from AI_Employee_Vault/Inbox, analyzes content,
creates step-by-step Plan.md in AI_Employee_Vault/Needs_Action.
Integrates with vault-file-manager for moving processed files.
Idempotent - processes each file once.
Callable by watcher or scheduler triggers.

Usage:
    python scripts/task_planner.py           # Process all new files
    python scripts/task_planner.py --file <filename.md>  # Process specific file
    python scripts/task_planner.py --dry-run  # Preview without changes

Features:
- Idempotent processing (same file processed once)
- Callable interface for watcher/scheduler integration
- Integrates with vault-file-manager
- Comprehensive action logging
- Dry-run mode for testing
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent

# Define folder paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# File paths
ACTION_LOG_FILE = LOGS_DIR / "action.log"
ERROR_LOG_FILE = LOGS_DIR / "watcher_errors.log"
PLANNER_TRACKER_FILE = LOGS_DIR / "planner_processed.txt"


# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def ensure_folders() -> None:
    """Ensure all required folders exist"""
    for folder in [INBOX_DIR, NEEDS_ACTION_DIR, DONE_DIR, LOGS_DIR]:
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
        print(f"[CRITICAL] Failed to log error: {e}", file=sys.stderr)


# =============================================================================
# TRACKER UTILITIES
# =============================================================================

def load_processed_files() -> Set[str]:
    """Load the set of already processed filenames"""
    try:
        if PLANNER_TRACKER_FILE.exists():
            with open(PLANNER_TRACKER_FILE, "r") as f:
                return set(line.strip() for line in f if line.strip())
    except Exception as e:
        log_error(f"Failed to load planner processed tracker: {e}")
    return set()


def save_processed_file(filename: str) -> None:
    """Save a filename to the processed tracker"""
    try:
        ensure_folders()
        with open(PLANNER_TRACKER_FILE, "a") as f:
            f.write(filename + "\n")
    except Exception as e:
        log_error(f"Failed to save processed file '{filename}': {e}")


def is_file_processed(filename: str, processed_files: Set[str]) -> bool:
    """Check if a file has already been processed"""
    return filename in processed_files


# =============================================================================
# FILE ANALYSIS
# =============================================================================

def parse_frontmatter(content: str) -> Dict[str, Any]:
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


def analyze_file_content(filepath: Path) -> Dict[str, Any]:
    """
    Analyze a markdown file and extract planning information.
    
    Returns:
        dict: Analysis results including frontmatter, content summary, and suggested steps
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        frontmatter = parse_frontmatter(content)
        
        # Get content without frontmatter
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()
        
        # Analyze content for action items
        analysis = {
            "filename": filepath.name,
            "frontmatter": frontmatter,
            "content_length": len(body),
            "content_preview": body[:200] + "..." if len(body) > 200 else body,
            "type": frontmatter.get("type", "general"),
            "priority": frontmatter.get("priority", "medium"),
            "status": frontmatter.get("status", "pending"),
            "created_at": frontmatter.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "related_files": frontmatter.get("related_files", ""),
            "suggested_steps": generate_suggested_steps(body, frontmatter)
        }
        
        return analysis
        
    except Exception as e:
        log_error(f"Failed to analyze file '{filepath.name}': {e}")
        return {
            "filename": filepath.name,
            "frontmatter": {},
            "content_length": 0,
            "content_preview": "",
            "type": "unknown",
            "priority": "medium",
            "status": "pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "related_files": "",
            "suggested_steps": ["Error: Could not analyze file content"],
            "error": str(e)
        }


def generate_suggested_steps(content: str, frontmatter: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate suggested execution steps based on content analysis"""
    steps = []
    task_type = frontmatter.get("type", "general").lower()
    
    # Type-specific step generation
    if task_type in ["file_review", "review"]:
        steps = [
            {
                "action": "Review file content",
                "details": "Read and understand the file's purpose and key information",
                "output": "Summary of file contents"
            },
            {
                "action": "Categorize and tag",
                "details": "Identify file type, add relevant tags for future reference",
                "output": "Categorized file with metadata"
            },
            {
                "action": "Determine next action",
                "details": "Decide if file needs archiving, further processing, or response",
                "output": "Action decision documented"
            }
        ]
    elif task_type in ["client_request", "client"]:
        steps = [
            {
                "action": "Analyze client requirements",
                "details": "Extract key deliverables, deadlines, and expectations",
                "output": "Requirements list"
            },
            {
                "action": "Draft response or action plan",
                "details": "Create initial response addressing client needs",
                "output": "Response draft in Drafts/"
            },
            {
                "action": "Schedule follow-up",
                "details": "Set reminders and calendar events based on deadlines",
                "output": "Calendar entries created"
            }
        ]
    elif task_type in ["document", "documentation"]:
        steps = [
            {
                "action": "Review document structure",
                "details": "Analyze document organization and completeness",
                "output": "Structure assessment"
            },
            {
                "action": "Process document content",
                "details": "Extract, transform, or integrate document data",
                "output": "Processed content"
            },
            {
                "action": "Archive with metadata",
                "details": "Store in appropriate location with proper indexing",
                "output": "Archived document"
            }
        ]
    elif task_type in ["task", "action_item"]:
        steps = [
            {
                "action": "Understand task requirements",
                "details": "Parse task description and identify success criteria",
                "output": "Task breakdown"
            },
            {
                "action": "Execute task steps",
                "details": "Perform required actions in logical order",
                "output": "Task completion"
            },
            {
                "action": "Verify and document",
                "details": "Confirm task completion and record outcomes",
                "output": "Completion report"
            }
        ]
    else:
        # Generic steps for unknown types
        steps = [
            {
                "action": "Review content",
                "details": "Read and understand the file's purpose",
                "output": "Content summary"
            },
            {
                "action": "Identify required actions",
                "details": "Determine what needs to be done based on content",
                "output": "Action list"
            },
            {
                "action": "Execute and archive",
                "details": "Complete actions and move to appropriate folder",
                "output": "Completed and archived"
            }
        ]
    
    return steps


# =============================================================================
# PLAN GENERATION
# =============================================================================

def generate_plan_content(analysis: Dict[str, Any]) -> str:
    """Generate the full Plan.md content based on analysis"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build steps section
    steps_md = ""
    for i, step in enumerate(analysis.get("suggested_steps", []), 1):
        steps_md += f"""
### Step {i}: {step.get('action', 'Unknown Action')}
- **Action:** {step.get('action', 'N/A')}
- **Details:** {step.get('details', 'N/A')}
- **Expected Output:** {step.get('output', 'N/A')}
"""
    
    # Build resources section
    resources = [
        "- [ ] Access to source file",
        "- [ ] Required permissions verified",
        "- [ ] Backup location available"
    ]
    
    # Build risks section
    risks = []
    if analysis.get("priority") == "high":
        risks.append("- ⚠️ High priority - expedite processing")
    if analysis.get("content_length", 0) > 5000:
        risks.append("- ℹ️ Large file - may require additional processing time")
    if analysis.get("type") == "unknown":
        risks.append("- ⚠️ Unknown file type - manual review may be needed")
    if not risks:
        risks.append("- ✅ No significant risks identified")
    
    plan_content = f"""---
type: execution_plan
status: pending
priority: {analysis.get('priority', 'medium')}
created_at: {timestamp}
source_file: {analysis.get('filename', 'unknown')}
---

# Plan: {analysis.get('filename', 'Unknown File')}

## Source Analysis

- **File:** {analysis.get('filename', 'unknown')}
- **Type:** {analysis.get('type', 'general')}
- **Priority:** {analysis.get('priority', 'medium')}
- **Detected:** {analysis.get('created_at', 'unknown')}

## Content Preview

```
{analysis.get('content_preview', 'No preview available')}
```

## Step-by-Step Execution Plan
{steps_md}

## Required Resources

{chr(10).join(resources)}

## Risks & Considerations

{chr(10).join(risks)}

## Completion Criteria

- [ ] All steps executed
- [ ] Output verified
- [ ] Files archived appropriately

---
*Generated by Task Planner on {timestamp}*
"""
    
    return plan_content


def create_plan_file(analysis: Dict[str, Any], dry_run: bool = False) -> Optional[Path]:
    """
    Create Plan.md file in Needs_Action folder.
    
    Args:
        analysis: File analysis results
        dry_run: If True, don't actually write the file
        
    Returns:
        Path to created file, or None if dry_run
    """
    try:
        ensure_folders()
        
        # Generate plan filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = analysis.get('filename', 'unknown').replace('.md', '')
        plan_filename = f"Plan_{source_name}_{timestamp}.md"
        plan_filepath = NEEDS_ACTION_DIR / plan_filename
        
        # Generate and write plan content
        plan_content = generate_plan_content(analysis)
        
        if not dry_run:
            with open(plan_filepath, "w", encoding='utf-8') as f:
                f.write(plan_content)
            log_action(f"TASK_PLANNER: Created {plan_filename} in Needs_Action")
            return plan_filepath
        else:
            print(f"[DRY-RUN] Would create: {plan_filepath}")
            return None
            
    except Exception as e:
        log_error(f"Failed to create plan file: {e}")
        return None


# =============================================================================
# FILE MANAGEMENT (Vault File Manager Integration)
# =============================================================================

def move_to_done(filepath: Path, dry_run: bool = False) -> bool:
    """
    Move a file from Inbox to Done folder.
    Integrates with vault-file-manager pattern.
    
    Args:
        filepath: Path to file to move
        dry_run: If True, don't actually move
        
    Returns:
        bool: True if successful
    """
    try:
        ensure_folders()
        
        if not filepath.exists():
            log_error(f"File not found: {filepath}")
            return False
        
        dest_path = DONE_DIR / filepath.name
        
        if dry_run:
            print(f"[DRY-RUN] Would move: {filepath} -> {dest_path}")
            return True
        
        # Move the file
        shutil.move(str(filepath), str(dest_path))
        log_action(f"TASK_PLANNER: Moved {filepath.name} to Done")
        return True
        
    except Exception as e:
        log_error(f"Failed to move file '{filepath.name}' to Done: {e}")
        return False


# =============================================================================
# MAIN PLANNER CLASS
# =============================================================================

class TaskPlanner:
    """
    Task Planner - Callable interface for processing inbox files.
    
    Usage:
        planner = TaskPlanner()
        planner.process_inbox()
        
        # Or process specific file
        planner.process_file("example.md")
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.processed_files: Set[str] = set()
        self.files_processed = 0
        self.plans_created = 0
        self.files_moved = 0
        self.errors = 0
        
    def load_tracker(self) -> None:
        """Load processed files tracker"""
        self.processed_files = load_processed_files()
        
    def process_inbox(self) -> Dict[str, int]:
        """
        Process all new .md files in Inbox.
        
        Returns:
            dict: Statistics about processing
        """
        self.load_tracker()
        
        if not INBOX_DIR.exists():
            print(f"[INFO] Inbox folder does not exist: {INBOX_DIR}")
            log_action("TASK_PLANNER: Inbox folder does not exist")
            return self._get_stats()
        
        # Get all .md files in Inbox
        inbox_files = [f for f in INBOX_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".md"]
        
        if not inbox_files:
            print("[INFO] No .md files in Inbox to process")
            log_action("TASK_PLANNER: No .md files in Inbox")
            return self._get_stats()
        
        print(f"Found {len(inbox_files)} .md file(s) in Inbox")
        log_action(f"TASK_PLANNER: Found {len(inbox_files)} .md file(s) to analyze")
        
        for filepath in inbox_files:
            self.process_file(filepath)
        
        return self._get_stats()
    
    def process_file(self, filepath: Path) -> bool:
        """
        Process a single file.
        
        Args:
            filepath: Path to file to process
            
        Returns:
            bool: True if processed successfully
        """
        filename = filepath.name
        
        # Check if already processed (idempotent)
        if is_file_processed(filename, self.processed_files):
            print(f"[SKIP] Already processed: {filename}")
            return False
        
        print(f"\n[PROCESS] {filename}")
        log_action(f"TASK_PLANNER: Analyzing {filename}")
        
        try:
            # Analyze file content
            analysis = analyze_file_content(filepath)
            
            if "error" in analysis:
                print(f"[ERROR] Failed to analyze: {filename}")
                self.errors += 1
                return False
            
            # Create plan file
            plan_path = create_plan_file(analysis, dry_run=self.dry_run)
            if plan_path:
                self.plans_created += 1
                print(f"[PLAN] Created: {plan_path.name}")
            
            # Move original file to Done
            if move_to_done(filepath, dry_run=self.dry_run):
                self.files_moved += 1
                print(f"[MOVED] {filename} -> Done/")
            
            # Mark as processed
            if not self.dry_run:
                save_processed_file(filename)
                self.processed_files.add(filename)
            
            self.files_processed += 1
            return True
            
        except Exception as e:
            log_error(f"Error processing '{filename}': {e}")
            self.errors += 1
            print(f"[ERROR] {filename}: {e}")
            return False
    
    def _get_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        return {
            "files_processed": self.files_processed,
            "plans_created": self.plans_created,
            "files_moved": self.files_moved,
            "errors": self.errors
        }
    
    def print_summary(self) -> None:
        """Print processing summary"""
        stats = self._get_stats()
        
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║              ✅ Task Planner Complete                     ║
╠══════════════════════════════════════════════════════════╣
║  Files processed: {stats['files_processed']:<37} ║
║  Plans created: {stats['plans_created']:<38} ║
║  Files moved to Done: {stats['files_moved']:<32} ║
║  Errors: {stats['errors']:<46} ║
╚══════════════════════════════════════════════════════════╝
"""
        print(summary)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Task Planner - Analyze inbox files and create execution plans"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Process a specific file (default: process all)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview actions without making changes"
    )
    
    args = parser.parse_args()
    
    # Initialize planner
    planner = TaskPlanner(dry_run=args.dry_run)
    
    if args.dry_run:
        print("[DRY-RUN MODE] No changes will be made\n")
    
    # Process files
    if args.file:
        # Process specific file
        filepath = INBOX_DIR / args.file
        if filepath.exists():
            planner.process_file(filepath)
        else:
            print(f"[ERROR] File not found: {filepath}")
            sys.exit(1)
    else:
        # Process all files in Inbox
        planner.process_inbox()
    
    # Print summary
    planner.print_summary()
    
    # Exit with error code if there were errors
    if planner.errors > 0:
        sys.exit(1)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
