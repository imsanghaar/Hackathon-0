#!/usr/bin/env python3
"""
CEO Briefing Weekly Scheduler

Schedules the CEO briefing report to run automatically every week.
Integrates with schedular-silvertier for execution.

Usage:
    python schedule_ceo_briefing.py --install    # Install weekly schedule
    python schedule_ceo_briefing.py --run        # Run briefing immediately
    python schedule_ceo_briefing.py --status     # Check schedule status
    python schedule_ceo_briefing.py --uninstall  # Remove schedule
"""

import argparse
import os
import sys
import subprocess
import json
from datetime import datetime

# Configuration
BASE_DIR = r"E:\ai_employee\Hackathon-0"
SCRIPTS_DIR = os.path.join(BASE_DIR, ".claude", "skills", "ceo-briefing", "scripts")
SCHEDULE_FILE = os.path.join(BASE_DIR, ".claude", "skills", "ceo-briefing", "schedule.json")
LOG_FILE = os.path.join(BASE_DIR, "Logs", "ceo_briefing_scheduler.log")
BRIEFING_SCRIPT = os.path.join(SCRIPTS_DIR, "generate_ceo_briefing.py")

# Ensure directories exist
os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log_message(message):
    """Log a message to the scheduler log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    print(log_entry.strip())


def run_briefing():
    """Run the CEO briefing generation script."""
    log_message("Starting CEO briefing generation...")
    
    try:
        result = subprocess.run(
            [sys.executable, BRIEFING_SCRIPT],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode == 0:
            log_message(f"CEO briefing generated successfully: {result.stdout.strip()}")
            return True
        else:
            log_message(f"CEO briefing generation failed: {result.stderr.strip()}")
            return False
    
    except Exception as e:
        log_message(f"Error running CEO briefing: {str(e)}")
        return False


def save_schedule(day_of_week=0, hour=9, minute=0):
    """
    Save the schedule configuration.
    
    Args:
        day_of_week: 0=Monday, 6=Sunday
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0-59)
    """
    schedule_config = {
        "enabled": True,
        "day_of_week": day_of_week,
        "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week],
        "hour": hour,
        "minute": minute,
        "installed_at": datetime.now().isoformat(),
        "last_run": None,
        "run_count": 0
    }
    
    with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
        json.dump(schedule_config, f, indent=2)
    
    log_message(f"Schedule saved: Every {schedule_config['day_name']} at {hour:02d}:{minute:02d}")
    return schedule_config


def load_schedule():
    """Load the schedule configuration."""
    if not os.path.exists(SCHEDULE_FILE):
        return None
    
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Error loading schedule: {e}")
        return None


def install_schedule(day_of_week=0, hour=9, minute=0):
    """
    Install the weekly schedule.

    For production use, this would integrate with:
    - Windows Task Scheduler (Windows)
    - cron (Linux/macOS)
    - Or the internal schedular-silvertier
    """
    # Save schedule config
    config = save_schedule(day_of_week, hour, minute)

    day_name = config['day_name']

    print("=" * 60)
    print("         CEO Briefing Schedule Installed")
    print("=" * 60)
    print(f"Frequency: Weekly")
    print(f"Day: {day_name}")
    print(f"Time: {hour:02d}:{minute:02d}")
    print(f"Log: Logs/ceo_briefing_scheduler.log")
    print("=" * 60)
    print("")
    print("To complete setup, add to your system scheduler:")
    print("")
    print("Windows Task Scheduler:")
    print("1. Open Task Scheduler")
    print("2. Create Basic Task: 'CEO Weekly Briefing'")
    print(f"3. Trigger: Weekly on {day_name} at {hour:02d}:{minute:02d}")
    print("4. Action: Start a program")
    print("   - Program: python")
    print(f"   - Arguments: {BRIEFING_SCRIPT}")
    print(f"   - Start in: {BASE_DIR}")
    print("")
    print("Linux/macOS Cron:")
    print("1. Run: crontab -e")
    print(f"2. Add: {minute} {hour} * * {day_of_week + 1} python3 {BRIEFING_SCRIPT}")
    print("")
    print("Or use internal schedular-silvertier:")
    print("Add ceo-briefing to the scheduler rotation.")
    print("")
    print(f"Schedule configuration saved to: {SCHEDULE_FILE}")

    log_message(f"Weekly schedule installed: {day_name} at {hour:02d}:{minute:02d}")
    return True


def uninstall_schedule():
    """Remove the schedule configuration."""
    if os.path.exists(SCHEDULE_FILE):
        os.remove(SCHEDULE_FILE)
        log_message("Schedule configuration removed.")
        print("✅ Schedule uninstalled. System scheduler entries must be removed manually.")
    else:
        print("ℹ️ No schedule configuration found.")
    return True


def show_status():
    """Show the current schedule status."""
    config = load_schedule()

    print("=" * 60)
    print("         CEO Briefing Scheduler Status")
    print("=" * 60)

    if config:
        status = "Enabled" if config.get('enabled', False) else "Disabled"
        last_run = config.get('last_run', 'Never')
        run_count = config.get('run_count', 0)

        print(f"Status: {status}")
        print(f"Schedule: Every {config.get('day_name', 'N/A')} at {config.get('hour', 0):02d}:{config.get('minute', 0):02d}")
        print(f"Installed: {config.get('installed_at', 'Unknown')[:19]}")
        print(f"Last Run: {str(last_run)[:19]}")
        print(f"Total Runs: {run_count}")
    else:
        print("Status: Not configured")
        print("")
        print("Run with --install to set up weekly schedule")

    print("=" * 60)
    print(f"Log file: {LOG_FILE}")

    # Show recent log entries
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-5:]
                if lines:
                    print("\nRecent log entries:")
                    for line in lines:
                        print(f"  {line.strip()}")
        except Exception:
            pass


def update_last_run():
    """Update the schedule with the last run time."""
    config = load_schedule()
    if config:
        config['last_run'] = datetime.now().isoformat()
        config['run_count'] = config.get('run_count', 0) + 1
        
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        log_message(f"Last run updated. Total runs: {config['run_count']}")


# =============================================================================
# Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CEO Briefing Weekly Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python schedule_ceo_briefing.py --install              # Install default schedule (Monday 9 AM)
  python schedule_ceo_briefing.py --install --day 4      # Install on Friday
  python schedule_ceo_briefing.py --run                  # Run briefing now
  python schedule_ceo_briefing.py --status               # Show status
  python schedule_ceo_briefing.py --uninstall            # Remove schedule
        """
    )
    
    parser.add_argument('--install', action='store_true',
                        help='Install weekly schedule')
    parser.add_argument('--run', action='store_true',
                        help='Run CEO briefing immediately')
    parser.add_argument('--status', action='store_true',
                        help='Show schedule status')
    parser.add_argument('--uninstall', action='store_true',
                        help='Remove schedule')
    parser.add_argument('--day', type=int, default=0, choices=range(7),
                        help='Day of week (0=Monday, 6=Sunday). Default: 0 (Monday)')
    parser.add_argument('--hour', type=int, default=9, choices=range(24),
                        help='Hour in 24h format. Default: 9')
    parser.add_argument('--minute', type=int, default=0, choices=range(60),
                        help='Minute. Default: 0')
    
    args = parser.parse_args()
    
    if args.run:
        success = run_briefing()
        if success:
            update_last_run()
        sys.exit(0 if success else 1)
    
    elif args.install:
        install_schedule(args.day, args.hour, args.minute)
        sys.exit(0)
    
    elif args.status:
        show_status()
        sys.exit(0)
    
    elif args.uninstall:
        uninstall_schedule()
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
