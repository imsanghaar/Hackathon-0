#!/usr/bin/env python3
"""
AI Employee System - Unified Interactive CLI
Bronze Tier - Production Ready

A beautiful, interactive terminal interface with:
- Smooth animations and transitions
- Real-time file monitoring with live updates
- Colorful dashboard with statistics
- Interactive menu navigation
- Integrated file watcher
- Task processing with progress indicators

Usage:
    python ai_employee.py

Commands:
    python ai_employee.py              # Run interactive CLI
    python ai_employee.py --watch      # Run file watcher in background
    python ai_employee.py --dashboard  # Run live dashboard only

Requirements:
    pip install -r requirements.txt
"""

import os
import sys
import time
import threading
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

# Rich library for beautiful terminal UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich import box
from rich.live import Live as RichLive

# Colorama for Windows color support
from colorama import init as colorama_init

# Initialize colorama for Windows
colorama_init()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.resolve()

# Define folder paths
INBOX_FOLDER = BASE_DIR / "Inbox"
NEEDS_ACTION_FOLDER = BASE_DIR / "Needs_Action"
DONE_FOLDER = BASE_DIR / "Done"
LOGS_FOLDER = BASE_DIR / "Logs"
PLANS_FOLDER = BASE_DIR / "Plans"

# File paths
DASHBOARD_FILE = BASE_DIR / "Dashboard.md"
SYSTEM_LOG_FILE = BASE_DIR / "System_Log.md"
COMPANY_HANDBOOK_FILE = BASE_DIR / "Company_Handbook.md"
PROCESSED_TRACKER_FILE = LOGS_FOLDER / "processed_files.txt"
ERROR_LOG_FILE = LOGS_FOLDER / "watcher_errors.log"

# Check intervals
CHECK_INTERVAL = 2  # Real-time monitoring check interval
WATCH_INTERVAL = 5  # File watcher check interval


# =============================================================================
# DATA UTILITIES
# =============================================================================

class VaultData:
    """Utilities for reading and managing vault data"""
    
    @staticmethod
    def ensure_folders():
        """Ensure all required folders exist"""
        for folder in [INBOX_FOLDER, NEEDS_ACTION_FOLDER, DONE_FOLDER, LOGS_FOLDER, PLANS_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_inbox_files() -> List[str]:
        """Get all files in Inbox folder"""
        if not INBOX_FOLDER.exists():
            return []
        return sorted([f.name for f in INBOX_FOLDER.iterdir() if f.is_file()])
    
    @staticmethod
    def get_pending_tasks() -> List[Dict[str, Any]]:
        """Get all pending tasks from Needs_Action folder"""
        tasks = []
        if not NEEDS_ACTION_FOLDER.exists():
            return tasks
        
        for task_file in sorted(NEEDS_ACTION_FOLDER.glob("*.md")):
            try:
                content = task_file.read_text()
                task_info = {
                    "filename": task_file.name,
                    "path": str(task_file),
                    "content": content,
                    "type": "unknown",
                    "status": "pending",
                    "priority": "medium",
                    "created_at": "unknown"
                }
                
                # Parse frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1].strip()
                        for line in frontmatter.split("\n"):
                            if ":" in line:
                                key, value = line.split(":", 1)
                                key = key.strip()
                                value = value.strip()
                                if key in task_info:
                                    task_info[key] = value
                
                tasks.append(task_info)
            except Exception:
                continue
        
        return tasks
    
    @staticmethod
    def get_completed_tasks() -> List[str]:
        """Get list of completed tasks from Done folder"""
        if not DONE_FOLDER.exists():
            return []
        return sorted([f.name for f in DONE_FOLDER.iterdir() if f.is_file()])
    
    @staticmethod
    def get_dashboard_content() -> str:
        """Read dashboard content"""
        if DASHBOARD_FILE.exists():
            return DASHBOARD_FILE.read_text()
        return "# Dashboard\n\nNo dashboard available."
    
    @staticmethod
    def get_system_log_content() -> str:
        """Read system log content"""
        if SYSTEM_LOG_FILE.exists():
            return SYSTEM_LOG_FILE.read_text()
        return "# System Log\n\nNo logs available."
    
    @staticmethod
    def get_statistics() -> Dict[str, int]:
        """Get vault statistics"""
        return {
            "inbox_files": len(VaultData.get_inbox_files()),
            "pending_tasks": len(VaultData.get_pending_tasks()),
            "completed_tasks": len(VaultData.get_completed_tasks()),
            "plans": len(list(PLANS_FOLDER.glob("*.md"))) if PLANS_FOLDER.exists() else 0
        }
    
    @staticmethod
    def load_processed_files() -> set:
        """Load the list of processed files"""
        try:
            if PROCESSED_TRACKER_FILE.exists():
                with open(PROCESSED_TRACKER_FILE, "r") as f:
                    return set(line.strip() for line in f if line.strip())
        except Exception:
            pass
        return set()
    
    @staticmethod
    def save_processed_file(filename: str) -> None:
        """Save a filename to processed tracker"""
        try:
            with open(PROCESSED_TRACKER_FILE, "a") as f:
                f.write(filename + "\n")
        except Exception:
            pass
    
    @staticmethod
    def log_error(error_message: str) -> None:
        """Log an error to the error log file"""
        try:
            LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_entry = f"[{timestamp}] {error_message}\n"
            with open(ERROR_LOG_FILE, "a") as f:
                f.write(error_entry)
        except Exception:
            pass
    
    @staticmethod
    def update_dashboard_for_completion(task_count: int) -> None:
        """Update Dashboard.md after processing tasks"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Read current dashboard
        if DASHBOARD_FILE.exists():
            content = DASHBOARD_FILE.read_text()
        else:
            content = "# Dashboard\n\n## Pending Tasks\n\n- *No pending tasks*\n\n## Completed Tasks\n\n## System Notes\n\n- *No system notes*\n"
        
        # Update pending tasks section
        pending_tasks = VaultData.get_pending_tasks()
        if pending_tasks:
            pending_list = "\n".join([f"- [ ] {t['filename']}" for t in pending_tasks])
            content = content.replace(
                "## Pending Tasks\n\n",
                f"## Pending Tasks\n\n{pending_list}\n\n"
            )
        else:
            content = content.replace(
                "## Pending Tasks\n\n",
                "## Pending Tasks\n\n- *No pending tasks*\n\n"
            )
        
        DASHBOARD_FILE.write_text(content)
        
        # Update system log
        log_entry = f"| {timestamp} | Process Tasks | Completed {task_count} task(s) via Interactive CLI |\n"
        
        if SYSTEM_LOG_FILE.exists():
            log_content = SYSTEM_LOG_FILE.read_text()
            if "| Date | Action | Details |" in log_content:
                log_content = log_content.replace(
                    "| Date | Action | Details |",
                    f"| Date | Action | Details |\n{log_entry}"
                )
        else:
            log_content = f"# System Log\n\n## Activity Log\n\n| Date | Action | Details |\n{log_entry}"
        
        SYSTEM_LOG_FILE.write_text(log_content)


# =============================================================================
# FILE WATCHER
# =============================================================================

class FileWatcher:
    """File watcher with real-time monitoring"""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.console = Console()
        self.processed_files: set = set()
    
    def start(self) -> None:
        """Start watching in background thread"""
        VaultData.ensure_folders()
        self.processed_files = VaultData.load_processed_files()
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        self.console.print(f"[dim]👁️ File watcher started - Monitoring Inbox/[/dim]")
    
    def stop(self) -> None:
        """Stop watching"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.console.print(f"[dim]⏹️ File watcher stopped[/dim]")
    
    def _watch_loop(self) -> None:
        """Main watch loop"""
        while self.running:
            try:
                if not INBOX_FOLDER.exists():
                    time.sleep(WATCH_INTERVAL)
                    continue
                
                current_files = {f.name for f in INBOX_FOLDER.iterdir() if f.is_file()}
                
                for filename in current_files:
                    if filename not in self.processed_files:
                        # New file detected!
                        self._create_task(filename)
                        self.processed_files.add(filename)
                        VaultData.save_processed_file(filename)
                        
                        if self.callback:
                            self.callback(f"new:{filename}")
                
                time.sleep(WATCH_INTERVAL)
                
            except Exception as e:
                VaultData.log_error(f"Watcher error: {e}")
                time.sleep(WATCH_INTERVAL)
    
    def _create_task(self, filename: str) -> None:
        """Create a task file for new inbox file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            safe_name = filename.replace(" ", "_")
            task_filename = f"task_{safe_name}.md"
            task_filepath = NEEDS_ACTION_FOLDER / task_filename
            
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
            
            with open(task_filepath, "w") as f:
                f.write(content)
            
            if self.callback:
                self.callback(f"task_created:{filename}")
                
        except Exception as e:
            VaultData.log_error(f"Failed to create task for '{filename}': {e}")


# =============================================================================
# UI COMPONENTS
# =============================================================================

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def header(live: bool = False) -> Panel:
        """Create header panel with real-time clock"""
        title = Text()
        title.append("🤖 AI Employee System ", style="bold bright_cyan")
        title.append("| By ISC ", style="dim yellow")
        if live:
            title.append("| 📡 Live Monitor", style="dim yellow")
        else:
            title.append("| Bronze Tier", style="dim white")

        # Real-time clock with seconds
        subtitle = f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return Panel(
            Text(f"{title}\n{subtitle}", justify="center"),
            title="[bold blue]══════════════════════════════[/bold blue]",
            border_style="bright_blue",
            box=box.DOUBLE,
            padding=(0, 2)
        )
    
    @staticmethod
    def stats_panel(stats: Dict[str, int]) -> Panel:
        """Create statistics panel"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold white", justify="right")
        
        icons = {
            "inbox_files": "📥",
            "pending_tasks": "⏳",
            "completed_tasks": "✅",
            "plans": "📋"
        }
        
        colors = {
            "inbox_files": "yellow",
            "pending_tasks": "red",
            "completed_tasks": "green",
            "plans": "blue"
        }
        
        for key, value in stats.items():
            icon = icons.get(key, "•")
            color = colors.get(key, "white")
            display_name = key.replace("_", " ").title()
            table.add_row(f"{icon} {display_name}", f"[{color}]{value}[/{color}]")
        
        return Panel(
            table,
            title="[bold]📊 Statistics[/bold]",
            border_style="bright_yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    @staticmethod
    def inbox_panel(files: List[str]) -> Panel:
        """Create inbox files panel"""
        if not files:
            return Panel(
                Text("📭 Inbox is empty", style="dim italic", justify="center"),
                title="[bold]📥 Inbox[/bold]",
                border_style="green",
                box=box.ROUNDED
            )
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Filename", style="cyan")
        table.add_column("Status", style="yellow", width=10)
        
        for i, filename in enumerate(files, 1):
            # Escape filename for Rich markup
            safe_filename = filename.replace('[', '[[').replace(']', ']]')
            table.add_row(str(i), safe_filename[:40], "[yellow]New[/yellow]")
        
        return Panel(
            table,
            title="[bold]📥 Inbox[/bold]",
            border_style="bright_green",
            padding=(0, 1)
        )
    
    @staticmethod
    def tasks_panel(tasks: List[Dict[str, Any]], scroll_offset: int = 0, visible_rows: int = 6) -> Panel:
        """Create pending tasks panel with scroll support"""
        if not tasks:
            return Panel(
                Text("✓ No pending tasks", style="green italic", justify="center"),
                title="[bold]⏳ Pending Tasks[/bold]",
                border_style="green",
                box=box.ROUNDED
            )

        table = Table(show_header=True, box=box.ROUNDED, expand=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Task", style="cyan", no_wrap=False)
        table.add_column("Type", style="magenta", width=12)
        table.add_column("Priority", style="yellow", width=10)

        priority_colors = {"high": "bold red", "medium": "bold yellow", "low": "bold green"}

        # Calculate visible range for scrolling
        total_tasks = len(tasks)
        start_idx = max(0, min(scroll_offset, total_tasks - visible_rows))
        end_idx = min(start_idx + visible_rows, total_tasks)
        
        # Show scroll indicators if needed
        title = f"[bold]⏳ Pending Tasks ({total_tasks})[/bold]"
        if total_tasks > visible_rows:
            if start_idx > 0:
                title += f" [dim]↑ {start_idx} above[/dim]"
            if end_idx < total_tasks:
                title += f" [dim]{total_tasks - end_idx} below ↓[/dim]"

        # Add visible tasks
        for i in range(start_idx, end_idx):
            task = tasks[i]
            priority = task.get("priority", "medium")
            color = priority_colors.get(priority, "white")
            # Escape filename for Rich markup
            name = task["filename"].replace('[', '[[').replace(']', ']]')
            if len(name) > 30:
                name = name[:27] + "..."
            table.add_row(
                str(i + 1),
                name,
                task.get("type", "unknown"),
                f"[{color}]{priority}[/{color}]"
            )

        # Add scroll hint if there are more tasks
        if total_tasks > visible_rows:
            table.add_row(
                "",
                f"[dim]... {total_tasks - visible_rows} more task(s) - Use Option [2] to view all ...[/dim]",
                "",
                ""
            )

        return Panel(
            table,
            title=title,
            border_style="bright_red",
            padding=(0, 1)
        )
    
    @staticmethod
    def menu_panel(auto_refresh: bool = True) -> Panel:
        """Create interactive menu panel"""
        menu_items = [
            ("[1]", "📥 View Inbox", "View files in Inbox"),
            ("[2]", "⏳ View Tasks", "View pending tasks"),
            ("[3]", "▶️ Process Tasks", "Process all pending tasks"),
            ("[4]", "📋 Create Plan", "Generate task plan"),
            ("[5]", "📊 Dashboard", "View full dashboard"),
            ("[6]", "📝 System Log", "View system logs"),
            ("[7]", "🔄 Refresh", "Refresh all data"),
            ("[q]", "🚪 Quit", "Exit the application"),
        ]
        
        text = Text()
        for key, icon, description in menu_items:
            text.append(f"{key} {icon} ", style="bold cyan")
            text.append(f"{description}\n", style="white")
        
        if auto_refresh:
            text.append("\n", style="dim")
            text.append("🔄 Auto-refresh active (every 3s) ", style="bold green")
            text.append("| ", style="dim")
            text.append("👁️ File watcher running", style="bold cyan")
        
        return Panel(
            text,
            title="[bold]🎯 Main Menu[/bold]",
            border_style="bright_magenta",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    @staticmethod
    def notification(message: str, style: str = "info") -> Panel:
        """Create notification panel"""
        styles = {
            "info": ("Info", "blue"),
            "success": ("Success", "green"),
            "warning": ("Warning", "yellow"),
            "error": ("Error", "red")
        }

        label, color = styles.get(style, ("Note", "white"))
        
        # Escape Rich markup in message
        safe_message = message.replace('[', '[[').replace(']', ']]')

        return Panel(
            f"[bold {color}]{label}[/bold {color}]  {safe_message}",
            border_style=color,
            box=box.ROUNDED,
            padding=(0, 2)
        )
    
    @staticmethod
    def activity_panel(notifications: List[Dict[str, str]]) -> Panel:
        """Create activity notifications panel"""
        if not notifications:
            return Panel(
                Text("No recent activity", style="dim italic", justify="center"),
                title="[bold]📬 Activity[/bold]",
                border_style="dim",
                box=box.ROUNDED
            )
        
        text = Text()
        for notif in notifications[:5]:
            icon = "📥" if notif["type"] == "success" else "⚠️"
            color = "green" if notif["type"] == "success" else "yellow"
            text.append(f"[{color}][{notif['time']}] {icon} {notif['message']}[/{color}]\n")
        
        return Panel(
            text,
            title="[bold]📬 Recent Activity[/bold]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class AIEmployeeCLI:
    """Main unified CLI application"""
    
    def __init__(self, mode: str = "interactive"):
        self.console = Console()
        self.mode = mode  # "interactive", "dashboard", "watch"
        self.running = True
        self.stats = {}
        self.inbox_files = []
        self.pending_tasks = []
        self.notifications: List[Dict[str, str]] = []
        self.watcher: Optional[FileWatcher] = None
        self.auto_refresh_thread: Optional[threading.Thread] = None
        self.refresh_interval = 3  # Refresh every 3 seconds
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_data(self) -> None:
        """Load current vault data"""
        VaultData.ensure_folders()
        self.stats = VaultData.get_statistics()
        self.inbox_files = VaultData.get_inbox_files()
        self.pending_tasks = VaultData.get_pending_tasks()
    
    def handle_event(self, event: str) -> None:
        """Handle file watcher events"""
        if event.startswith("new:"):
            filename = event[4:]
            self.notifications.insert(0, {
                "type": "success",
                "message": f"New file detected: {filename}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            self.notifications = self.notifications[:5]
        elif event.startswith("task_created:"):
            filename = event[13:]
            self.notifications.insert(0, {
                "type": "info",
                "message": f"Task created for: {filename}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            self.notifications = self.notifications[:5]
    
    def start_auto_refresh(self) -> None:
        """Start background auto-refresh thread"""
        self.auto_refresh_thread = threading.Thread(target=self._auto_refresh_loop, daemon=True)
        self.auto_refresh_thread.start()
    
    def stop_auto_refresh(self) -> None:
        """Stop background auto-refresh thread"""
        self.running = False
        if self.auto_refresh_thread:
            self.auto_refresh_thread.join(timeout=2)
    
    def _auto_refresh_loop(self) -> None:
        """Background loop to refresh data periodically"""
        while self.running:
            try:
                # Only refresh stats, not the display (display is refreshed on demand)
                self.stats = VaultData.get_statistics()
                self.inbox_files = VaultData.get_inbox_files()
                self.pending_tasks = VaultData.get_pending_tasks()
            except Exception:
                pass
            time.sleep(self.refresh_interval)
    
    def display_dashboard(self) -> Layout:
        """Create dashboard layout"""
        self.load_data()
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=12)
        )
        
        layout["header"].update(UIComponents.header(live=(self.mode == "dashboard")))
        
        body = Layout()
        body.split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        body["left"].update(UIComponents.stats_panel(self.stats))
        
        tasks_body = Layout()
        tasks_body.split_column(
            Layout(name="inbox", size=10),
            Layout(name="tasks")
        )
        tasks_body["inbox"].update(UIComponents.inbox_panel(self.inbox_files))
        tasks_body["tasks"].update(UIComponents.tasks_panel(self.pending_tasks))
        
        body["right"].update(tasks_body)
        layout["body"].update(body)
        layout["footer"].update(UIComponents.menu_panel(auto_refresh=True))
        
        return layout

    def process_tasks_action(self) -> None:
        """Process all pending tasks - Professional workflow with external AI agent"""
        if not self.pending_tasks:
            self.console.print(UIComponents.notification("No pending tasks to process", "info"))
            return
        
        # Stop watcher and auto-refresh temporarily
        if self.watcher:
            self.watcher.stop()
        self.stop_auto_refresh()
        
        self.console.print()
        self.console.print(Panel(
            Text(
                "📋 TASK PROCESSING WORKFLOW\n\n"
                "Open any CLI agent (Gemini, Claude, Qwen) and ask it to:\n"
                "  'Process Tasks'\n\n"
                "The AI agent will:\n"
                "  • Read all task files in Needs_Action/\n"
                "  • Mark each task as completed\n"
                "  • Move files to Done/\n"
                "  • Update Dashboard.md and System_Log.md\n\n"
                "When done, press any key to continue...",
                justify="center"
            ),
            title="[bold cyan]🤖 AI Agent Required[/bold cyan]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        
        # Wait for user to return
        input()
        
        # Reload data to reflect any changes made by external AI
        self.load_data()
        
        # Restart watcher and auto-refresh
        self.watcher = FileWatcher(callback=self.handle_event)
        self.watcher.start()
        self.start_auto_refresh()
        
        self.console.print()
        self.console.print(UIComponents.notification("Welcome back! Data refreshed.", "success"))
        self.console.print(f"[dim]Current pending tasks: {len(self.pending_tasks)}[/dim]")
        self.console.print()
        input("Press Enter to return to menu...")

    def create_plan_action(self) -> None:
        """Create a planning document"""
        if not self.pending_tasks:
            self.console.print(UIComponents.notification("No pending tasks to plan", "info"))
            return
        
        self.console.print(UIComponents.notification("Creating plan document...", "info"))
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plan_filename = f"Plan_{timestamp}.md"
        plan_path = PLANS_FOLDER / plan_filename
        
        PLANS_FOLDER.mkdir(parents=True, exist_ok=True)
        
        plan_content = f"""# Plan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary of Pending Tasks

Total pending tasks: {len(self.pending_tasks)}

"""
        for i, task in enumerate(self.pending_tasks, 1):
            plan_content += f"{i}. **{task['filename']}** (Type: {task.get('type', 'unknown')}, Priority: {task.get('priority', 'medium')})\n"
        
        plan_content += f"""
## Suggested Order of Execution

1. Process high priority tasks first
2. Group similar task types together
3. Handle file review tasks before general tasks

## Risks or Unclear Items

- Review each task carefully before execution
- Confirm any destructive actions

## Strategy

Process tasks in batches by type. Start with file reviews as they may provide context for other tasks.
Log all actions in System_Log.md for tracking.

---
*Generated by Interactive CLI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        plan_path.write_text(plan_content)
        self.console.print(UIComponents.notification(f"Plan created: {plan_filename}", "success"))
    
    def run_interactive(self) -> None:
        """Run interactive mode with real-time clock"""
        self.clear_screen()

        self.console.print()
        with self.console.status("[bold cyan]🚀 Starting AI Employee System...[/bold cyan]", spinner="dots"):
            time.sleep(1.5)

        # Start file watcher in background
        self.watcher = FileWatcher(callback=self.handle_event)
        self.watcher.start()

        # Start auto-refresh in background
        self.start_auto_refresh()

        self.clear_screen()

        while self.running:
            # Display dashboard with current time (updates each loop iteration)
            layout = self.display_dashboard()
            self.console.print(layout)

            self.console.print()
            choice = Prompt.ask(
                "[bold cyan]Enter your choice[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "q"],
                default="7"
            )

            self.console.print()

            if choice == "1":
                self.view_inbox_action()
            elif choice == "2":
                self.view_tasks_action()
            elif choice == "3":
                self.process_tasks_action()
            elif choice == "4":
                self.create_plan_action()
                input("\nPress Enter to continue...")
            elif choice == "5":
                self.view_dashboard_action()
            elif choice == "6":
                self.view_system_log_action()
            elif choice == "7":
                self.console.print(UIComponents.notification("Refreshing data...", "info"))
                self.load_data()
                time.sleep(0.5)
            elif choice.lower() == "q":
                self.console.print()
                self.console.print(UIComponents.notification("Thank you for using AI Employee System! Goodbye! 👋", "info"))
                self.running = False

        if self.watcher:
            self.watcher.stop()
        self.stop_auto_refresh()
    
    def run_dashboard(self) -> None:
        """Run live dashboard mode"""
        self.clear_screen()
        
        self.console.print()
        with self.console.status("[bold cyan]🚀 Starting Live Dashboard...[/bold cyan]", spinner="dots"):
            time.sleep(1.0)
        
        self.clear_screen()
        
        # Start file watcher
        self.watcher = FileWatcher(callback=self.handle_event)
        self.watcher.start()
        
        # Start auto-refresh
        self.start_auto_refresh()
        
        self.console.print("[green]✓ Live Dashboard started - Press Ctrl+C to exit[/green]\n")
        
        def generate_display():
            # Data is already refreshed in background, just use current values
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=4),
                Layout(name="body"),
                Layout(name="footer", size=3)
            )
            
            layout["header"].update(UIComponents.header(live=True))
            
            body = Layout()
            body.split_row(
                Layout(name="stats", ratio=1),
                Layout(name="activity", ratio=2)
            )
            body["stats"].update(UIComponents.stats_panel(self.stats))
            body["activity"].update(UIComponents.activity_panel(self.notifications))
            
            layout["body"].update(body)
            
            footer_text = Text("Press Ctrl+C to exit | Auto-refresh enabled (3s) | File watcher active", style="dim italic", justify="center")
            layout["footer"].update(Panel(footer_text, border_style="dim", box=box.ROUNDED))
            
            return layout
        
        try:
            with RichLive(generate_display, console=self.console, refresh_per_second=2) as live:
                while self.running:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped by user[/yellow]")
        finally:
            if self.watcher:
                self.watcher.stop()
            self.stop_auto_refresh()
    
    def view_inbox_action(self) -> None:
        """View inbox files"""
        self.console.print()
        if self.inbox_files:
            table = Table(title="📥 Inbox Files", box=box.ROUNDED)
            table.add_column("#", style="dim")
            table.add_column("Filename", style="cyan")
            table.add_column("Full Path", style="dim")
            
            for i, filename in enumerate(self.inbox_files, 1):
                table.add_row(str(i), filename, str(INBOX_FOLDER / filename))
            
            self.console.print(table)
        else:
            self.console.print("[dim]📭 Inbox is empty[/dim]")
        
        self.console.print()
        input("\nPress Enter to continue...")
    
    def view_tasks_action(self) -> None:
        """View pending tasks with scrollable interface"""
        self.console.print()
        
        if not self.pending_tasks:
            self.console.print("[green]✓ No pending tasks[/green]")
            self.console.print()
            input("\nPress Enter to continue...")
            return
        
        # Scrollable view for tasks
        scroll_offset = 0
        visible_rows = 15  # Number of rows visible at once
        total_tasks = len(self.pending_tasks)
        
        priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        
        while True:
            self.clear_screen()
            self.console.print()
            self.console.print(f"[bold cyan]⏳ Pending Tasks ({scroll_offset + 1}-{min(scroll_offset + visible_rows, total_tasks)} of {total_tasks})[/bold cyan]")
            self.console.print()
            
            # Calculate visible range
            start_idx = scroll_offset
            end_idx = min(scroll_offset + visible_rows, total_tasks)
            
            # Create table for visible tasks
            table = Table(box=box.ROUNDED, expand=True)
            table.add_column("#", style="dim", width=4)
            table.add_column("Task File", style="cyan", no_wrap=False)
            table.add_column("Type", style="magenta", width=12)
            table.add_column("Priority", style="yellow", width=10)
            table.add_column("Status", style="green", width=10)
            
            for i in range(start_idx, end_idx):
                task = self.pending_tasks[i]
                priority = task.get("priority", "medium")
                icon = priority_icons.get(priority, "⚪")
                
                # Escape filename for Rich markup
                safe_filename = task["filename"].replace('[', '[[').replace(']', ']]')

                table.add_row(
                    str(i + 1),
                    safe_filename,
                    task.get("type", "unknown"),
                    f"{icon} {priority}",
                    task.get("status", "pending")
                )
            
            self.console.print(table)
            
            # Navigation hints
            self.console.print()
            if total_tasks > visible_rows:
                nav_text = "[bold]Navigation:[/bold] "
                if scroll_offset > 0:
                    nav_text += "[cyan][U]p[/cyan] "
                if end_idx < total_tasks:
                    nav_text += "[cyan][D]own[/cyan] "
                nav_text += "| [green][Enter][/green] Back to Menu"
                self.console.print(f"[dim]{nav_text}[/dim]")
                self.console.print()
                
                choice = Prompt.ask(
                    "Scroll",
                    choices=["u", "d", ""],
                    default="",
                    show_choices=False
                )
                
                if choice.lower() == "u" and scroll_offset > 0:
                    scroll_offset = max(0, scroll_offset - visible_rows)
                elif choice.lower() == "d" and end_idx < total_tasks:
                    scroll_offset = min(total_tasks - visible_rows, scroll_offset + visible_rows)
                else:
                    break
            else:
                self.console.print("[dim]Press Enter to go back[/dim]")
                input()
                break
        
        self.console.print()
        input("\nPress Enter to continue...")
    
    def view_dashboard_action(self) -> None:
        """View full dashboard content"""
        self.console.print()
        self.console.print(Panel(
            VaultData.get_dashboard_content(),
            title="[bold]📊 Dashboard[/bold]",
            border_style="blue",
            box=box.ROUNDED
        ))
        self.console.print()
        input("\nPress Enter to continue...")
    
    def view_system_log_action(self) -> None:
        """View system log content"""
        self.console.print()
        self.console.print(Panel(
            VaultData.get_system_log_content(),
            title="[bold]📝 System Log[/bold]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        self.console.print()
        input("\nPress Enter to continue...")
    
    def run(self) -> None:
        """Run the appropriate mode"""
        try:
            if self.mode == "dashboard":
                self.run_dashboard()
            else:
                self.run_interactive()
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user.")
        except Exception as e:
            # Print error as plain text to avoid Rich markup issues
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.watcher:
                self.watcher.stop()


# =============================================================================
# ENTRY POINT
# =============================================================================

def print_banner():
    """Print startup banner"""
    console = Console()
    banner = """
+==========================================================+
|         AI Employee System - Bronze Tier                 |
|     Interactive CLI with Real-time Monitoring            |
+==========================================================+
"""
    console.print("[bold cyan]" + banner + "[/bold cyan]")


def main():
    """Main entry point"""
    console = Console()
    
    # Parse arguments
    mode = "interactive"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--dashboard":
            mode = "dashboard"
        elif sys.argv[1] == "--watch":
            # Just run watcher mode
            console.print("[cyan]Starting file watcher only...[/cyan]")
            VaultData.ensure_folders()
            watcher = FileWatcher()
            watcher.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                watcher.stop()
                console.print("[yellow]Watcher stopped[/yellow]")
            return
    
    print_banner()
    
    app = AIEmployeeCLI(mode=mode)
    app.run()


if __name__ == "__main__":
    main()
