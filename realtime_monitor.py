#!/usr/bin/env python3
"""
Real-time Monitor - Bronze Tier
Provides live monitoring capabilities with animated updates for the Interactive CLI.

Features:
- Live file system monitoring with instant updates
- Animated notifications for new files
- Real-time statistics updates
- Background threading for non-blocking monitoring

Usage:
    from realtime_monitor import RealtimeMonitor
    
    monitor = RealtimeMonitor()
    monitor.start()  # Start monitoring in background
    monitor.stop()   # Stop monitoring
"""

import os
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.spinner import Spinner
from rich.table import Table
from rich import box

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent.resolve()
INBOX_FOLDER = BASE_DIR / "Inbox"
NEEDS_ACTION_FOLDER = BASE_DIR / "Needs_Action"
DONE_FOLDER = BASE_DIR / "Done"
LOGS_FOLDER = BASE_DIR / "Logs"

CHECK_INTERVAL = 2  # Check every 2 seconds for real-time feel


# =============================================================================
# MONITOR CLASSES
# =============================================================================

class FileMonitor:
    """Monitor file system changes in real-time"""
    
    def __init__(self, folder: Path, callback: Optional[Callable[[str], None]] = None):
        self.folder = folder
        self.callback = callback
        self.known_files: set = set()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.console = Console()
    
    def start(self) -> None:
        """Start monitoring in background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.console.print(f"[dim]👁️ Monitoring: {self.folder.name}/[/dim]")
    
    def stop(self) -> None:
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.console.print(f"[dim]⏹️ Stopped monitoring: {self.folder.name}[/dim]")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        # Initial scan
        if self.folder.exists():
            self.known_files = {f.name for f in self.folder.iterdir() if f.is_file()}
        
        while self.running:
            try:
                if not self.folder.exists():
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                current_files = {f.name for f in self.folder.iterdir() if f.is_file()}
                
                # Check for new files
                new_files = current_files - self.known_files
                for filename in new_files:
                    if self.callback:
                        self.callback(f"new:{filename}")
                    self.known_files.add(filename)
                
                # Check for removed files
                removed_files = self.known_files - current_files
                for filename in removed_files:
                    if self.callback:
                        self.callback(f"removed:{filename}")
                    self.known_files.discard(filename)
                
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                self.console.print(f"[red]Monitor error: {e}[/red]")
                time.sleep(CHECK_INTERVAL)


class RealtimeMonitor:
    """Main real-time monitoring system with live updates"""
    
    def __init__(self):
        self.console = Console()
        self.running = False
        self.callbacks: List[Callable[[str, Any], None]] = []
        self.monitors: List[FileMonitor] = []
        self.stats: Dict[str, int] = {}
        self.notifications: List[Dict[str, str]] = []
        self.max_notificationss = 5
    
    def add_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Add a callback for real-time updates"""
        self.callbacks.append(callback)
    
    def notify(self, event_type: str, data: Any) -> None:
        """Send notification to all callbacks"""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.console.print(f"[dim]Callback error: {e}[/dim]")
    
    def start(self) -> None:
        """Start all monitors"""
        self.running = True
        
        # Create inbox monitor
        inbox_monitor = FileMonitor(
            INBOX_FOLDER,
            callback=lambda e: self._handle_inbox_event(e)
        )
        inbox_monitor.start()
        self.monitors.append(inbox_monitor)
        
        self.console.print("[green]✓ Real-time monitoring started[/green]")
    
    def stop(self) -> None:
        """Stop all monitors"""
        self.running = False
        for monitor in self.monitors:
            monitor.stop()
        self.monitors.clear()
        self.console.print("[yellow]⏹️ Real-time monitoring stopped[/yellow]")
    
    def _handle_inbox_event(self, event: str) -> None:
        """Handle inbox file events"""
        if event.startswith("new:"):
            filename = event[4:]
            self.notifications.insert(0, {
                "type": "success",
                "message": f"📥 New file detected: {filename}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            self.notify("inbox_new", filename)
        elif event.startswith("removed:"):
            filename = event[8:]
            self.notifications.insert(0, {
                "type": "warning",
                "message": f"📤 File removed: {filename}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            self.notify("inbox_removed", filename)
        
        # Keep only recent notifications
        self.notifications = self.notifications[:self.max_notificationss]
    
    def get_stats(self) -> Dict[str, int]:
        """Get current statistics"""
        return {
            "inbox_files": len(list(INBOX_FOLDER.iterdir())) if INBOX_FOLDER.exists() else 0,
            "pending_tasks": len(list(NEEDS_ACTION_FOLDER.glob("*.md"))) if NEEDS_ACTION_FOLDER.exists() else 0,
            "completed_tasks": len(list(DONE_FOLDER.iterdir())) if DONE_FOLDER.exists() else 0,
        }
    
    def create_live_display(self) -> Live:
        """Create a live display for real-time updates"""
        def generate_display() -> Panel:
            stats = self.get_stats()
            
            text = Text()
            text.append("📊 Real-time Statistics\n\n", style="bold cyan")
            text.append(f"📥 Inbox: ", style="white")
            text.append(f"{stats['inbox_files']}\n", style="bold yellow")
            text.append(f"⏳ Pending: ", style="white")
            text.append(f"{stats['pending_tasks']}\n", style="bold red")
            text.append(f"✅ Completed: ", style="white")
            text.append(f"{stats['completed_tasks']}\n", style="bold green")
            
            if self.notifications:
                text.append("\n📬 Recent Activity\n", style="bold cyan")
                for notif in self.notifications[:3]:
                    icon = "✓" if notif["type"] == "success" else "⚠"
                    color = "green" if notif["type"] == "success" else "yellow"
                    text.append(f"[{color}] [{notif['time']}] {icon} {notif['message']}[/{color}]\n")
            
            return Panel(
                text,
                title="[bold]🔄 Live Monitor[/bold]",
                border_style="bright_cyan",
                box=box.ROUNDED,
                padding=(1, 2)
            )
        
        return Live(generate_display(), console=self.console, refresh_per_second=2)


# =============================================================================
# LIVE DASHBOARD
# =============================================================================

class LiveDashboard:
    """Live updating dashboard with real-time data"""
    
    def __init__(self, monitor: RealtimeMonitor):
        self.monitor = monitor
        self.console = Console()
        self.running = False
    
    def _create_header(self) -> Panel:
        """Create animated header"""
        title = Text()
        title.append("🤖 AI Employee System ", style="bold bright_cyan")
        title.append("| Live Dashboard", style="dim white")
        
        return Panel(
            Text(f"{title}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", justify="center"),
            title="[bold blue]══════════════════════════════[/bold blue]",
            border_style="bright_blue",
            box=box.DOUBLE,
            padding=(0, 2)
        )
    
    def _create_stats_panel(self) -> Panel:
        """Create live statistics panel"""
        stats = self.monitor.get_stats()
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white", justify="right")
        
        table.add_row("📥 Inbox Files", f"[yellow]{stats['inbox_files']}[/yellow]")
        table.add_row("⏳ Pending Tasks", f"[red]{stats['pending_tasks']}[/red]")
        table.add_row("✅ Completed Tasks", f"[green]{stats['completed_tasks']}[/green]")
        
        return Panel(
            table,
            title="[bold]📊 Statistics[/bold]",
            border_style="bright_yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    def _create_notifications_panel(self) -> Panel:
        """Create notifications panel"""
        if not self.monitor.notifications:
            return Panel(
                Text("No recent activity", style="dim italic", justify="center"),
                title="[bold]📬 Activity[/bold]",
                border_style="dim",
                box=box.ROUNDED
            )
        
        text = Text()
        for notif in self.monitor.notifications[:5]:
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
    
    def _generate_layout(self) -> Layout:
        """Generate full dashboard layout"""
        from rich.layout import Layout
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["header"].update(self._create_header())
        
        body = Layout()
        body.split_row(
            Layout(name="stats", ratio=1),
            Layout(name="activity", ratio=2)
        )
        body["stats"].update(self._create_stats_panel())
        body["activity"].update(self._create_notifications_panel())
        
        layout["body"].update(body)
        
        footer_text = Text("Press Ctrl+C to exit | Auto-refresh enabled", style="dim italic", justify="center")
        layout["footer"].update(Panel(footer_text, border_style="dim", box=box.ROUNDED))
        
        return layout
    
    def run(self) -> None:
        """Run live dashboard"""
        self.running = True
        self.monitor.start()
        
        def generate_display():
            return self._generate_layout()
        
        try:
            with Live(generate_display(), console=self.console, refresh_per_second=2) as live:
                while self.running:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.monitor.stop()


# =============================================================================
# QUICK START
# =============================================================================

def run_live_dashboard():
    """Quick function to run the live dashboard"""
    console = Console()
    console.print("[cyan]🚀 Starting Live Dashboard...[/cyan]")
    
    monitor = RealtimeMonitor()
    dashboard = LiveDashboard(monitor)
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped by user[/yellow]")


if __name__ == "__main__":
    run_live_dashboard()
