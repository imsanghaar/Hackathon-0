#!/usr/bin/env python3
"""
Interactive CLI - Bronze Tier
A beautiful, production-ready interactive terminal interface for the AI Employee System.

Features:
- Smooth animations and transitions
- Real-time updates with live file monitoring
- Colorful dashboard with statistics
- Interactive menu navigation
- Keyboard shortcuts for quick actions

Usage:
    python interactive_cli.py

Requirements:
    pip install -r requirements.txt
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Rich library for beautiful terminal UI
from rich.console import Console, Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.animation import Animation
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.keypad import Keypad
from rich.style import Style
from rich import box

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

# ANSI color codes for custom styling
class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    # Background colors
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"

# =============================================================================
# ANIMATION UTILITIES
# =============================================================================

class Animator:
    """Smooth animations for CLI"""
    
    @staticmethod
    def loading_dots(duration: float = 2.0, message: str = "Loading") -> None:
        """Display animated loading dots"""
        console = Console()
        end_time = time.time() + duration
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        with console.status(f"[cyan]{message}[/cyan]") as status:
            while time.time() < end_time:
                for dot in dots:
                    status.update(f"[cyan]{dot} {message}...[/cyan]")
                    time.sleep(0.08)
    
    @staticmethod
    def progress_bar(task_name: str, total: int = 100) -> None:
        """Display animated progress bar"""
        console = Console()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[green]{task_name}[/green]", total=total)
            for _ in range(total):
                progress.advance(task)
                time.sleep(0.02)
    
    @staticmethod
    def typing_effect(text: str, speed: float = 0.03) -> None:
        """Simulate typing effect for text"""
        console = Console()
        for char in text:
            console.print(char, end="", style="bold green")
            time.sleep(speed)
        console.print()
    
    @staticmethod
    def fade_in(text: str, style: str = "bold cyan") -> None:
        """Fade in text effect"""
        console = Console()
        console.print(f"[{style}]{text}[/{style}]")
    
    @staticmethod
    def success_checkmark(message: str = "Success!") -> None:
        """Display success animation with checkmark"""
        console = Console()
        console.print(f"\n[bold green]✓[/bold green] [green]{message}[/green]")
    
    @staticmethod
    def error_cross(message: str = "Error!") -> None:
        """Display error animation with cross"""
        console = Console()
        console.print(f"\n[bold red]✗[/bold red] [red]{message}[/red]")
    
    @staticmethod
    def spinner_animation(message: str, callback, *args, **kwargs) -> Any:
        """Run a callback with spinner animation"""
        console = Console()
        with console.status(f"[cyan]⠋ {message}[/cyan]", spinner="dots"):
            return callback(*args, **kwargs)


# =============================================================================
# DATA UTILITIES
# =============================================================================

class VaultData:
    """Utilities for reading and managing vault data"""
    
    @staticmethod
    def get_inbox_files() -> List[str]:
        """Get all files in Inbox folder"""
        if not INBOX_FOLDER.exists():
            return []
        return [f.name for f in INBOX_FOLDER.iterdir() if f.is_file()]
    
    @staticmethod
    def get_pending_tasks() -> List[Dict[str, Any]]:
        """Get all pending tasks from Needs_Action folder"""
        tasks = []
        if not NEEDS_ACTION_FOLDER.exists():
            return tasks
        
        for task_file in NEEDS_ACTION_FOLDER.glob("*.md"):
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
            except Exception as e:
                continue
        
        return tasks
    
    @staticmethod
    def get_completed_tasks() -> List[str]:
        """Get list of completed tasks from Done folder"""
        if not DONE_FOLDER.exists():
            return []
        return [f.name for f in DONE_FOLDER.iterdir() if f.is_file()]
    
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


# =============================================================================
# UI COMPONENTS
# =============================================================================

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def header() -> Panel:
        """Create animated header panel"""
        title = Text()
        title.append("🤖 AI Employee System ", style="bold bright_cyan")
        title.append("| Bronze Tier", style="dim white")
        
        subtitle = f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return Panel(
            Text(f"{title}\n{subtitle}", justify="center"),
            title="[bold blue]══════════════════════════════[/bold blue]",
            border_style="bright_blue",
            box=box.DOUBLE,
            padding=(1, 2)
        )
    
    @staticmethod
    def stats_panel(stats: Dict[str, int]) -> Panel:
        """Create statistics panel with animated numbers"""
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
            table.add_row(
                str(i),
                filename,
                "[yellow]New[/yellow]"
            )
        
        return Panel(
            table,
            title="[bold]📥 Inbox[/bold]",
            border_style="bright_green",
            padding=(0, 1)
        )
    
    @staticmethod
    def tasks_panel(tasks: List[Dict[str, Any]]) -> Panel:
        """Create pending tasks panel"""
        if not tasks:
            return Panel(
                Text("✓ No pending tasks", style="green italic", justify="center"),
                title="[bold]⏳ Pending Tasks[/bold]",
                border_style="green",
                box=box.ROUNDED
            )
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Task", style="cyan")
        table.add_column("Type", style="magenta", width=15)
        table.add_column("Priority", style="yellow", width=10)
        
        priority_colors = {
            "high": "red",
            "medium": "yellow",
            "low": "green"
        }
        
        for i, task in enumerate(tasks, 1):
            priority = task.get("priority", "medium")
            color = priority_colors.get(priority, "white")
            table.add_row(
                str(i),
                task["filename"][:40] + "..." if len(task["filename"]) > 40 else task["filename"],
                task.get("type", "unknown"),
                f"[{color}]{priority}[/{color}]"
            )
        
        return Panel(
            table,
            title=f"[bold]⏳ Pending Tasks ({len(tasks)})[/bold]",
            border_style="bright_red",
            padding=(0, 1)
        )
    
    @staticmethod
    def menu_panel() -> Panel:
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
            "info": ("ℹ️", "blue"),
            "success": ("✓", "green"),
            "warning": ("⚠", "yellow"),
            "error": ("✗", "red")
        }
        
        icon, color = styles.get(style, ("•", "white"))
        
        return Panel(
            f"[bold {color}]{icon} {message}[/{color}]",
            border_style=color,
            box=box.ROUNDED,
            padding=(0, 2)
        )
    
    @staticmethod
    def loading_panel(message: str) -> Panel:
        """Create loading panel with spinner"""
        return Panel(
            Spinner("dots", text=f"[cyan]{message}[/cyan]"),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class InteractiveCLI:
    """Main interactive CLI application"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
        self.stats = {}
        self.inbox_files = []
        self.pending_tasks = []
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_data(self) -> None:
        """Load current vault data"""
        self.stats = VaultData.get_statistics()
        self.inbox_files = VaultData.get_inbox_files()
        self.pending_tasks = VaultData.get_pending_tasks()
    
    def display_header(self) -> None:
        """Display animated header"""
        self.console.print()
        self.console.print(UIComponents.header())
        self.console.print()
    
    def display_dashboard(self) -> None:
        """Display main dashboard"""
        self.load_data()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body"),
            Layout(name="footer", size=12)
        )
        
        # Update sections
        layout["header"].update(UIComponents.header())
        
        # Body with stats and panels
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
        layout["footer"].update(UIComponents.menu_panel())
        
        self.console.print(layout)
    
    def process_tasks_action(self) -> None:
        """Process all pending tasks"""
        if not self.pending_tasks:
            self.console.print(UIComponents.notification("No pending tasks to process", "info"))
            return
        
        self.console.print(UIComponents.notification(f"Processing {len(self.pending_tasks)} task(s)...", "info"))
        
        # Show progress animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]Processing tasks...[/cyan]", total=len(self.pending_tasks))
            
            for i, pending_task in enumerate(self.pending_tasks):
                # Update task status to completed
                try:
                    content = pending_task["content"]
                    content = content.replace("status: pending", "status: completed")
                    
                    with open(pending_task["path"], "w") as f:
                        f.write(content)
                    
                    # Move to Done folder
                    dest_path = DONE_FOLDER / pending_task["filename"]
                    Path(pending_task["path"]).rename(dest_path)
                    
                    progress.update(task, description=f"[green]✓ {pending_task['filename']}[/green]")
                    progress.advance(task)
                    time.sleep(0.3)
                    
                except Exception as e:
                    progress.update(task, description=f"[red]✗ Error: {pending_task['filename']}[/red]")
                    time.sleep(0.3)
        
        # Update dashboard
        self.update_dashboard_completion()
        
        # Refresh data
        self.load_data()
        
        self.console.print()
        self.console.print(UIComponents.notification(f"Successfully processed {len(self.pending_tasks)} task(s)!", "success"))
    
    def update_dashboard_completion(self) -> None:
        """Update Dashboard.md with completed tasks"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Read current dashboard
        if DASHBOARD_FILE.exists():
            content = DASHBOARD_FILE.read_text()
        else:
            content = "# Dashboard\n\n## Pending Tasks\n\n- *No pending tasks*\n\n## Completed Tasks\n\n## System Notes\n\n- *No system notes*\n"
        
        # Update pending tasks section
        if self.pending_tasks:
            pending_list = "\n".join([f"- [ ] {t['filename']}" for t in self.pending_tasks])
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
        log_entry = f"| {timestamp} | Process Tasks | Completed {len(self.pending_tasks)} task(s) via Interactive CLI |\n"
        
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
    
    def create_plan_action(self) -> None:
        """Create a planning document"""
        if not self.pending_tasks:
            self.console.print(UIComponents.notification("No pending tasks to plan", "info"))
            return
        
        self.console.print(UIComponents.notification("Creating plan document...", "info"))
        
        # Generate plan
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plan_filename = f"Plan_{timestamp}.md"
        plan_path = PLANS_FOLDER / plan_filename
        
        # Ensure Plans folder exists
        PLANS_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Create plan content
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
    
    def view_inbox_action(self) -> None:
        """View inbox files"""
        self.console.print()
        if self.inbox_files:
            table = Table(title="📥 Inbox Files", box=box.ROUNDED)
            table.add_column("#", style="dim")
            table.add_column("Filename", style="cyan")
            table.add_column("Full Path", style="dim")
            
            for i, filename in enumerate(self.inbox_files, 1):
                table.add_row(
                    str(i),
                    filename,
                    str(INBOX_FOLDER / filename)
                )
            
            self.console.print(table)
        else:
            self.console.print("[dim]📭 Inbox is empty[/dim]")
        
        self.console.print()
        input("\nPress Enter to continue...")
    
    def view_tasks_action(self) -> None:
        """View pending tasks"""
        self.console.print()
        if self.pending_tasks:
            table = Table(title="⏳ Pending Tasks", box=box.ROUNDED)
            table.add_column("#", style="dim")
            table.add_column("Filename", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Priority", style="yellow")
            table.add_column("Status", style="green")
            
            for i, task in enumerate(self.pending_tasks, 1):
                table.add_row(
                    str(i),
                    task["filename"],
                    task.get("type", "unknown"),
                    task.get("priority", "medium"),
                    task.get("status", "pending")
                )
            
            self.console.print(table)
        else:
            self.console.print("[green]✓ No pending tasks[/green]")
        
        self.console.print()
        input("\nPress Enter to continue...")
    
    def run(self) -> None:
        """Main application loop"""
        self.clear_screen()
        
        # Welcome animation
        self.console.print()
        with self.console.status("[bold cyan]🚀 Starting AI Employee System...[/bold cyan]", spinner="dots"):
            time.sleep(1.5)
        
        self.clear_screen()
        
        while self.running:
            self.display_dashboard()
            
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
                if Confirm.ask("[yellow]Process all pending tasks?[/yellow]"):
                    self.process_tasks_action()
                    input("\nPress Enter to continue...")
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


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    try:
        app = InteractiveCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n[yellow]Application interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
