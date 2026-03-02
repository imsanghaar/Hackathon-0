#!/usr/bin/env python3
"""
Ralph Wiggum Autonomous Loop

Autonomous task execution with iterative planning and safety controls.

Behavior:
1. Analyze Task
2. Create Plan.md
3. Execute first step
4. Check Result
5. Continue next step
6. Repeat until completed
7. Move task to Done

Safety Features:
- Max 5 iterations per task
- Human approval required for risky actions
- State persistence for recovery

Integrates with existing schedular-silvertier.

Usage:
    python ralph_wiggum.py --run           # Run autonomous loop
    python ralph_wiggum.py --task <file>   # Process specific task
    python ralph_wiggum.py --status        # Show current status
    python ralph_wiggum.py --approve <id>  # Approve pending action
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
BASE_DIR = SCRIPT_DIR.parent.parent.parent.parent  # Go up to project root

# Folder paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
NEEDS_APPROVAL_DIR = VAULT_DIR / "Needs_Approval"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# File paths
STATE_FILE = SKILL_DIR / "state.json"
PLANS_DIR = SKILL_DIR / "plans"
ACTION_LOG = LOGS_DIR / "action.log"
ERROR_LOG = LOGS_DIR / "ralph_errors.log"
LOOP_LOG = LOGS_DIR / "ralph_loop.log"

# Safety settings
MAX_ITERATIONS = 5
APPROVAL_REQUIRED_KEYWORDS = [
    "delete", "remove", "drop", "destroy", "permanent",
    "payment", "transfer", "send money", "wire",
    "password", "secret", "credential", "api key",
    "approve", "authorize", "confirm"
]

# Ensure directories exist
for folder in [VAULT_DIR, INBOX_DIR, NEEDS_ACTION_DIR, NEEDS_APPROVAL_DIR, DONE_DIR, LOGS_DIR, PLANS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def log_action(message: str) -> None:
    """Log an action to action.log"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ACTION_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] RALPH: {message}\n")
    except Exception as e:
        print(f"[ERROR] Failed to log action: {e}")


def log_error(message: str) -> None:
    """Log an error to error log"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ERROR: {message}\n")
    except Exception as e:
        print(f"[ERROR] Failed to log error: {e}")


def log_loop(message: str, level: str = "INFO") -> None:
    """Log loop iteration to dedicated loop log"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOOP_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    except Exception as e:
        print(f"[ERROR] Failed to log loop: {e}")


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

def load_state() -> Dict[str, Any]:
    """Load the current state from file"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error(f"Failed to load state: {e}")
    
    return {
        "active_tasks": [],
        "completed_tasks": [],
        "pending_approvals": [],
        "current_iteration": 0,
        "last_run": None
    }


def save_state(state: Dict[str, Any]) -> None:
    """Save the current state to file"""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str)
    except Exception as e:
        log_error(f"Failed to save state: {e}")


# =============================================================================
# TASK ANALYSIS
# =============================================================================

def analyze_task(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a task file and extract key information.
    
    Returns:
        dict with task analysis results
    """
    result = {
        "filename": file_path.name,
        "path": str(file_path),
        "type": "unknown",
        "priority": "normal",
        "actions": [],
        "is_risky": False,
        "risk_reasons": [],
        "content": ""
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        result["content"] = content
        
        # Parse frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key == "type":
                            result["type"] = value
                        elif key == "priority":
                            result["priority"] = value
        
        # Extract actions from content
        action_patterns = [
            r"^\s*[-*]\s*(?:\[ \])?\s*(.+)$",  # Bullet points
            r"^\s*\d+\.\s*(.+)$",  # Numbered lists
            r"^\s*(?:action|step|task):\s*(.+)$",  # Explicit actions
        ]
        
        for line in content.split("\n"):
            for pattern in action_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    action = match.group(1).strip()
                    if action and len(action) > 3:
                        result["actions"].append(action)
        
        # Check for risky content
        content_lower = content.lower()
        for keyword in APPROVAL_REQUIRED_KEYWORDS:
            if keyword in content_lower:
                result["is_risky"] = True
                result["risk_reasons"].append(f"Contains '{keyword}'")
        
        # High priority tasks are also considered risky
        if result["priority"].lower() in ["high", "urgent", "critical"]:
            result["is_risky"] = True
            result["risk_reasons"].append(f"Priority: {result['priority']}")
        
        log_action(f"Analyzed task: {file_path.name} (type={result['type']}, risky={result['is_risky']})")
        
    except Exception as e:
        log_error(f"Failed to analyze task {file_path.name}: {e}")
        result["error"] = str(e)
    
    return result


# =============================================================================
# PLAN CREATION
# =============================================================================

def create_plan(task_analysis: Dict[str, Any]) -> Optional[Path]:
    """
    Create a step-by-step plan for the task.
    
    Returns:
        Path to the created plan file, or None if failed
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_filename = f"Plan_{task_analysis['filename'].replace('.md', '')}_{timestamp}.md"
        plan_path = PLANS_DIR / plan_filename
        
        # Generate steps from actions
        steps = []
        for i, action in enumerate(task_analysis.get("actions", [])[:5], 1):
            steps.append(f"""
### Step {i}: {action}
- **Status:** pending
- **Result:** 
- **Notes:** 
""")
        
        if not steps:
            steps.append("""
### Step 1: Review Task Content
- **Status:** pending
- **Result:**
- **Notes:** Analyze task requirements

### Step 2: Identify Required Actions
- **Status:** pending
- **Result:**
- **Notes:** Determine what needs to be done

### Step 3: Execute Primary Action
- **Status:** pending
- **Result:**
- **Notes:** Complete the main task

### Step 4: Verify Results
- **Status:** pending
- **Result:**
- **Notes:** Check if task completed successfully

### Step 5: Finalize and Archive
- **Status:** pending
- **Result:**
- **Notes:** Move to Done folder
""")
        
        plan_content = f"""---
type: autonomous_plan
status: active
created_at: {datetime.now().isoformat()}
source_task: {task_analysis['filename']}
task_type: {task_analysis['type']}
priority: {task_analysis['priority']}
is_risky: {task_analysis['is_risky']}
max_iterations: {MAX_ITERATIONS}
---

# Autonomous Plan: {task_analysis['filename']}

## Task Analysis

- **Source File:** {task_analysis['filename']}
- **Type:** {task_analysis['type']}
- **Priority:** {task_analysis['priority']}
- **Risk Level:** {'HIGH - Requires Approval' if task_analysis['is_risky'] else 'Normal'}
- **Analyzed At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Risk Assessment

"""
        
        if task_analysis['is_risky']:
            plan_content += "**Approval Required:** Yes\n\n"
            for reason in task_analysis.get('risk_reasons', []):
                plan_content += f"- ⚠️ {reason}\n"
        else:
            plan_content += "**Approval Required:** No\n\n"
        
        plan_content += """
## Execution Steps

"""
        
        plan_content += "".join(steps)
        
        plan_content += f"""
## Execution Log

| Iteration | Step | Status | Timestamp |
|-----------|------|--------|-----------|
| 0 | Plan Created | Complete | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

## Completion Status

- [ ] All steps executed
- [ ] Results verified
- [ ] Task moved to Done

---
*Generated by Ralph Wiggum Autonomous Loop*
"""
        
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(plan_content)
        
        log_action(f"Created plan: {plan_filename}")
        log_loop(f"Plan created: {plan_filename}")
        
        return plan_path
        
    except Exception as e:
        log_error(f"Failed to create plan: {e}")
        log_loop(f"Failed to create plan: {e}", "ERROR")
        return None


# =============================================================================
# STEP EXECION
# =============================================================================

def execute_step(plan_path: Path, step_number: int, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single step from the plan.
    
    Returns:
        dict with execution result
    """
    result = {
        "success": False,
        "step": step_number,
        "action": "",
        "output": "",
        "requires_approval": False,
        "error": None
    }
    
    try:
        # Read the plan
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the step
        step_pattern = rf"### Step {step_number}:[^\n]*\n(.*?)(?=### Step|$)"
        match = re.search(step_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not match:
            result["error"] = f"Step {step_number} not found"
            return result
        
        step_content = match.group(1)
        
        # Extract action
        action_match = re.search(r"\*\*Action:\*\*\s*(.+)", step_content)
        if action_match:
            result["action"] = action_match.group(1).strip()
        else:
            # Use the step header as action
            header_match = re.search(r"### Step \d+:\s*(.+)", match.group(0))
            if header_match:
                result["action"] = header_match.group(1).strip()
        
        # Check if approval is needed
        if result["action"]:
            action_lower = result["action"].lower()
            for keyword in APPROVAL_REQUIRED_KEYWORDS:
                if keyword in action_lower:
                    result["requires_approval"] = True
                    break
        
        # Simulate step execution (in real implementation, this would call appropriate skills)
        log_loop(f"Executing step {step_number}: {result['action'][:50]}...")
        
        # Update plan with execution status
        updated_content = content.replace(
            f"**Status:** pending",
            f"**Status:** completed",
            step_number
        )
        
        # Add to execution log
        log_entry = f"| {state.get('current_iteration', 1)} | Step {step_number} | Completed | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |\n"
        updated_content = updated_content.replace(
            "| Iteration | Step | Status | Timestamp |",
            f"| Iteration | Step | Status | Timestamp |\n{log_entry}"
        )
        
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        result["success"] = True
        result["output"] = f"Step {step_number} executed successfully"
        
        log_action(f"Executed step {step_number}: {result['action'][:50]}")
        log_loop(f"Step {step_number} completed successfully")
        
    except Exception as e:
        result["error"] = str(e)
        log_error(f"Failed to execute step {step_number}: {e}")
        log_loop(f"Step {step_number} failed: {e}", "ERROR")
    
    return result


# =============================================================================
# APPROVAL MANAGEMENT
# =============================================================================

def request_approval(task_analysis: Dict[str, Any], plan_path: Path) -> str:
    """
    Create an approval request for risky tasks.
    
    Returns:
        Approval request ID
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_id = f"ralph_{timestamp}"
        
        approval_content = f"""---
type: approval_request
status: pending
created_at: {datetime.now().isoformat()}
source: ralph-wiggum
priority: {task_analysis['priority']}
---

# Approval Request: {approval_id}

## Task Information

- **Original Task:** {task_analysis['filename']}
- **Type:** {task_analysis['type']}
- **Priority:** {task_analysis['priority']}

## Risk Assessment

This task has been flagged as requiring human approval due to:

"""
        
        for reason in task_analysis.get('risk_reasons', []):
            approval_content += f"- {reason}\n"
        
        approval_content += f"""
## Plan Location

{plan_path}

## Action Required

Please review the task and plan, then:

1. **To Approve:** Run `python ralph_wiggum.py --approve {approval_id}`
2. **To Reject:** Run `python ralph_wiggum.py --reject {approval_id}`

---
*Generated by Ralph Wiggum Autonomous Loop*
"""
        
        approval_path = NEEDS_APPROVAL_DIR / f"{approval_id}.md"
        
        with open(approval_path, "w", encoding="utf-8") as f:
            f.write(approval_content)
        
        log_action(f"Created approval request: {approval_id}")
        log_loop(f"Approval requested: {approval_id}")
        
        return approval_id
        
    except Exception as e:
        log_error(f"Failed to create approval request: {e}")
        return ""


def check_approval(approval_id: str) -> bool:
    """Check if an approval has been granted"""
    approval_path = NEEDS_APPROVAL_DIR / f"{approval_id}.md"
    
    if not approval_path.exists():
        return False
    
    try:
        with open(approval_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return "status: approved" in content.lower()
        
    except Exception:
        return False


# =============================================================================
# TASK COMPLETION
# =============================================================================

def complete_task(task_path: Path, plan_path: Path) -> bool:
    """
    Move completed task to Done folder.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Move task to Done
        done_path = DONE_DIR / task_path.name
        shutil.move(str(task_path), str(done_path))
        
        # Update plan status
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("status: active", "status: completed")
        content = content.replace("- [ ] All steps executed", "- [x] All steps executed")
        content = content.replace("- [ ] Results verified", "- [x] Results verified")
        content = content.replace("- [ ] Task moved to Done", "- [x] Task moved to Done")
        
        # Add completion timestamp
        completion_line = f"| {MAX_ITERATIONS} | Complete | Done | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |\n"
        content = content.replace("| Iteration | Step | Status | Timestamp |", 
                                  f"| Iteration | Step | Status | Timestamp |\n{completion_line}")
        
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Move plan to Done as well
        done_plan_path = DONE_DIR / plan_path.name
        shutil.move(str(plan_path), str(done_plan_path))
        
        log_action(f"Task completed: {task_path.name}")
        log_loop(f"Task completed and moved to Done: {task_path.name}")
        
        return True
        
    except Exception as e:
        log_error(f"Failed to complete task: {e}")
        log_loop(f"Failed to complete task: {e}", "ERROR")
        return False


# =============================================================================
# AUTONOMOUS LOOP
# =============================================================================

def run_autonomous_loop(task_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the autonomous loop for task processing.
    
    Args:
        task_file: Optional specific task file to process
    
    Returns:
        dict with loop results
    """
    result = {
        "tasks_processed": 0,
        "tasks_completed": 0,
        "tasks_pending_approval": 0,
        "errors": 0
    }
    
    log_loop("=" * 50)
    log_loop("Starting Ralph Wiggum Autonomous Loop")
    log_loop("=" * 50)
    
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    
    # Find tasks to process
    tasks_to_process = []
    
    if task_file:
        task_path = INBOX_DIR / task_file
        if task_path.exists():
            tasks_to_process.append(task_path)
    else:
        # Get all .md files in Inbox
        for file_path in INBOX_DIR.glob("*.md"):
            # Skip if already being processed
            if file_path.name not in [t.get("filename") for t in state.get("active_tasks", [])]:
                tasks_to_process.append(file_path)
    
    if not tasks_to_process:
        log_loop("No tasks to process")
        print("[INFO] No tasks to process")
        save_state(state)
        return result
    
    # Process each task
    for task_path in tasks_to_process:
        log_loop(f"Processing task: {task_path.name}")
        print(f"\n[LOOP] Processing: {task_path.name}")
        
        # Step 1: Analyze Task
        print("  [1/7] Analyzing task...")
        analysis = analyze_task(task_path)
        
        if "error" in analysis:
            result["errors"] += 1
            continue
        
        # Step 2: Create Plan.md
        print("  [2/7] Creating plan...")
        plan_path = create_plan(analysis)
        
        if not plan_path:
            result["errors"] += 1
            continue
        
        # Check if approval is needed
        if analysis["is_risky"]:
            print("  [!] Task requires approval - requesting...")
            approval_id = request_approval(analysis, plan_path)
            
            if approval_id:
                state.setdefault("pending_approvals", []).append({
                    "approval_id": approval_id,
                    "task": task_path.name,
                    "plan": str(plan_path),
                    "created_at": datetime.now().isoformat()
                })
                result["tasks_pending_approval"] += 1
                log_loop(f"Task {task_path.name} pending approval: {approval_id}")
                continue
        
        # Add to active tasks
        task_state = {
            "filename": task_path.name,
            "path": str(task_path),
            "plan": str(plan_path),
            "current_step": 1,
            "iteration": 0,
            "started_at": datetime.now().isoformat()
        }
        state.setdefault("active_tasks", []).append(task_state)
        result["tasks_processed"] += 1
        
        # Steps 3-6: Execute loop
        print("  [3-6/7] Executing autonomous loop...")
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            task_state["iteration"] = iteration
            state["current_iteration"] = iteration
            
            # Execute current step
            exec_result = execute_step(plan_path, task_state["current_step"], state)
            
            if not exec_result["success"]:
                log_loop(f"Iteration {iteration}: Step execution failed - {exec_result.get('error')}")
                break
            
            if exec_result["requires_approval"]:
                log_loop(f"Iteration {iteration}: Approval required for step")
                approval_id = request_approval(analysis, plan_path)
                if approval_id:
                    state.setdefault("pending_approvals", []).append({
                        "approval_id": approval_id,
                        "task": task_path.name,
                        "plan": str(plan_path),
                        "step": task_state["current_step"],
                        "created_at": datetime.now().isoformat()
                    })
                    result["tasks_pending_approval"] += 1
                break
            
            # Move to next step
            task_state["current_step"] += 1
            
            # Check if all steps completed
            if task_state["current_step"] > 5:
                print(f"  [7/7] Completing task...")
                
                # Step 7: Move to Done
                if complete_task(task_path, plan_path):
                    result["tasks_completed"] += 1
                    
                    # Remove from active tasks
                    state["active_tasks"] = [t for t in state["active_tasks"] if t["filename"] != task_path.name]
                    state.setdefault("completed_tasks", []).append({
                        "filename": task_path.name,
                        "completed_at": datetime.now().isoformat()
                    })
                
                break
        
        save_state(state)
    
    log_loop("=" * 50)
    log_loop(f"Loop completed: {result['tasks_completed']} completed, {result['tasks_pending_approval']} pending approval")
    log_loop("=" * 50)
    
    return result


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_status(args):
    """Show current status"""
    state = load_state()
    
    print("=" * 60)
    print("         Ralph Wiggum Autonomous Loop Status")
    print("=" * 60)
    
    print(f"\nActive Tasks: {len(state.get('active_tasks', []))}")
    for task in state.get("active_tasks", [])[:5]:
        print(f"  - {task['filename']} (Step {task['current_step']}, Iteration {task['iteration']})")
    
    print(f"\nPending Approvals: {len(state.get('pending_approvals', []))}")
    for approval in state.get("pending_approvals", [])[:5]:
        print(f"  - {approval['approval_id']}: {approval['task']}")
    
    print(f"\nCompleted Tasks: {len(state.get('completed_tasks', []))}")
    for task in state.get("completed_tasks", [])[-5:]:
        print(f"  - {task['filename']} ({task['completed_at'][:19]})")
    
    print(f"\nLast Run: {state.get('last_run', 'Never')[:19] if state.get('last_run') else 'Never'}")
    print(f"Max Iterations: {MAX_ITERATIONS}")
    
    print("\n" + "=" * 60)
    
    return 0


def cmd_approve(args):
    """Approve a pending action"""
    approval_id = args.approval_id
    
    approval_path = NEEDS_APPROVAL_DIR / f"{approval_id}.md"
    
    if not approval_path.exists():
        print(f"[ERROR] Approval request not found: {approval_id}")
        return 1
    
    try:
        with open(approval_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("status: pending", "status: approved")
        
        with open(approval_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Move to Done
        done_path = DONE_DIR / f"{approval_id}.md"
        shutil.move(str(approval_path), str(done_path))
        
        log_action(f"Approved: {approval_id}")
        print(f"[OK] Approved: {approval_id}")
        
        return 0
        
    except Exception as e:
        log_error(f"Failed to approve: {e}")
        print(f"[ERROR] Failed to approve: {e}")
        return 1


def cmd_reject(args):
    """Reject a pending action"""
    approval_id = args.approval_id
    
    approval_path = NEEDS_APPROVAL_DIR / f"{approval_id}.md"
    
    if not approval_path.exists():
        print(f"[ERROR] Approval request not found: {approval_id}")
        return 1
    
    try:
        with open(approval_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("status: pending", "status: rejected")
        
        with open(approval_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        log_action(f"Rejected: {approval_id}")
        print(f"[OK] Rejected: {approval_id}")
        
        return 0
        
    except Exception as e:
        log_error(f"Failed to reject: {e}")
        print(f"[ERROR] Failed to reject: {e}")
        return 1


def cmd_run(args):
    """Run the autonomous loop"""
    result = run_autonomous_loop(args.task if hasattr(args, 'task') else None)
    
    print("\n" + "=" * 60)
    print("         Loop Execution Results")
    print("=" * 60)
    print(f"Tasks Processed: {result['tasks_processed']}")
    print(f"Tasks Completed: {result['tasks_completed']}")
    print(f"Pending Approval: {result['tasks_pending_approval']}")
    print(f"Errors: {result['errors']}")
    print("=" * 60)
    
    return 0 if result["errors"] == 0 else 1


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Ralph Wiggum Autonomous Loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ralph_wiggum.py --run              # Run autonomous loop
  python ralph_wiggum.py --run --task file.md  # Process specific task
  python ralph_wiggum.py --status           # Show status
  python ralph_wiggum.py --approve ralph_123   # Approve pending action
  python ralph_wiggum.py --reject ralph_123    # Reject pending action
        """
    )

    # Commands
    parser.add_argument("--run", action="store_true", help="Run autonomous loop")
    parser.add_argument("--task", type=str, help="Specific task file to process")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--approve", type=str, metavar="ID", help="Approve pending action")
    parser.add_argument("--reject", type=str, metavar="ID", help="Reject pending action")

    args = parser.parse_args()

    # Handle commands
    if args.status:
        return cmd_status(args)
    elif args.approve:
        class Args:
            approval_id = args.approve
        return cmd_approve(Args())
    elif args.reject:
        class Args:
            approval_id = args.reject
        return cmd_reject(Args())
    elif args.run:
        return cmd_run(args)
    else:
        parser.print_help()
        return 0


# =============================================================================
# SCHEDULER INTEGRATION CLASS
# =============================================================================

class RalphWiggumLoop:
    """
    Ralph Wiggum Autonomous Loop class for scheduler integration.
    
    Usage:
        loop = RalphWiggumLoop()
        result = loop.run_loop(task_file)
    """
    
    def __init__(self):
        self.max_iterations = MAX_ITERATIONS
        self.state = load_state()
    
    def run_loop(self, task_path: Path) -> Dict[str, Any]:
        """
        Run autonomous loop for a single task.
        
        Args:
            task_path: Path to the task file
        
        Returns:
            dict with result status
        """
        result = {
            "status": "unknown",
            "completed": False,
            "pending_approval": False,
            "error": None
        }
        
        try:
            # Step 1: Analyze Task
            analysis = analyze_task(task_path)
            
            if "error" in analysis:
                result["status"] = "error"
                result["error"] = analysis["error"]
                return result
            
            # Step 2: Create Plan
            plan_path = create_plan(analysis)
            
            if not plan_path:
                result["status"] = "error"
                result["error"] = "Failed to create plan"
                return result
            
            # Check if approval needed
            if analysis["is_risky"]:
                approval_id = request_approval(analysis, plan_path)
                result["status"] = "pending_approval"
                result["pending_approval"] = True
                result["approval_id"] = approval_id
                return result
            
            # Steps 3-6: Execute loop
            for iteration in range(1, self.max_iterations + 1):
                # Execute step
                exec_result = execute_step(plan_path, iteration, self.state)
                
                if not exec_result["success"]:
                    result["status"] = "failed"
                    result["error"] = exec_result.get("error")
                    return result
                
                if exec_result["requires_approval"]:
                    approval_id = request_approval(analysis, plan_path)
                    result["status"] = "pending_approval"
                    result["pending_approval"] = True
                    result["approval_id"] = approval_id
                    return result
            
            # Step 7: Complete
            if complete_task(task_path, plan_path):
                result["status"] = "completed"
                result["completed"] = True
            
            return result
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            return result


if __name__ == "__main__":
    sys.exit(main())
