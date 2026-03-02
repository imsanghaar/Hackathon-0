
import argparse
import os
from datetime import datetime, timedelta
import glob
import subprocess

REPORT_FILE = "AI_Employee_Vault/Reports/CEO_Weekly.md"
LOG_DIR = "vault/Logs/"
ACCOUNTING_SCRIPT = "scripts/accounting_manager.py"

# --- Ensure Directories Exist ---
def ensure_directories():
    """Ensures necessary directories exist."""
    # Report directory
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    # Log directory (if not already created by MCP server)
    os.makedirs(LOG_DIR, exist_ok=True)
    # Accounting script directory (implicitly handled by script path)
    print("Directories ensured.")

# --- Data Gathering Functions ---
def get_tasks_completed(week_start_date, week_end_date):
    """Counts completed tasks based on files in AI_Employee_Vault/Done/ directory that were modified within the week."""
    completed_tasks_dir = "AI_Employee_Vault/Done/"
    count = 0
    recent_tasks = []
    try:
        if os.path.exists(completed_tasks_dir):
            for filename in os.listdir(completed_tasks_dir):
                file_path = os.path.join(completed_tasks_dir, filename)
                if os.path.isfile(file_path):
                    # Get last modification time
                    mod_timestamp = os.path.getmtime(file_path)
                    mod_date = datetime.fromtimestamp(mod_timestamp)
                    if week_start_date <= mod_date <= week_end_date:
                        count += 1
                        if len(recent_tasks) < 5: # List up to 5 recent tasks
                            recent_tasks.append(f"- {filename} (Completed: {mod_date.strftime('%Y-%m-%d')})")
        return count, recent_tasks
    except Exception as e:
        print(f"Error getting tasks completed: {e}")
        return 0, [f"Error retrieving task data: {e}"]

def get_emails_sent(week_start_date, week_end_date):
    """Counts emails sent from log files within the week."""
    email_log_patterns = [
        os.path.join(LOG_DIR, "emails_sent.log"),
        os.path.join(LOG_DIR, "gmail_watcher.log")
    ]
    total_emails = 0
    recent_emails = []
    try:
        for log_pattern in email_log_patterns:
            if os.path.exists(log_pattern):
                with open(log_pattern, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Basic check for email sent entries. This pattern might need refinement based on actual log format.
                        # Example log entry: [2026-03-02 10:00:00] [ACCOUNTING_SCRIPT] Email sent successfully to user@example.com
                        # Or from gmail_watcher: [2026-03-01 09:30:00] Gmail watcher: Processed email ID 12345, sent reply.
                        if "Email sent successfully" in line or "sent reply" in line:
                            try:
                                # Extract date from log line (assuming YYYY-MM-DD HH:MM:SS format at start of line)
                                log_date_str = line.split(']')[0].strip('[')
                                log_date = datetime.strptime(log_date_str.split(' ')[0], '%Y-%m-%d')
                                if week_start_date <= log_date <= week_end_date:
                                    total_emails += 1
                                    if len(recent_emails) < 5:
                                        recent_emails.append(f"- {line.strip()}")
                            except (ValueError, IndexError):
                                continue # Skip lines that don't match expected date format
        return total_emails, recent_emails
    except Exception as e:
        print(f"Error getting emails sent: {e}")
        return 0, [f"Error retrieving email logs: {e}"]

def get_linkedin_posts(week_start_date, week_end_date):
    """Counts LinkedIn posts from log files within the week."""
    linkedin_log_patterns = [
        os.path.join(LOG_DIR, "business.log") # Assuming MCP server logs LinkedIn posts here
        # Add other potential LinkedIn log files if they exist
    ]
    total_posts = 0
    recent_posts = []
    try:
        for log_pattern in linkedin_log_patterns:
            if os.path.exists(log_pattern):
                with open(log_pattern, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Example log entry: [2026-03-01 11:00:00] BUSINESS_ACTIVITY: LinkedIn post requested: This is my LinkedIn post content!...
                        if "BUSINESS_ACTIVITY: LinkedIn post requested:" in line:
                            try:
                                log_date_str = line.split(']')[0].strip('[')
                                log_date = datetime.strptime(log_date_str.split(' ')[0], '%Y-%m-%d')
                                if week_start_date <= log_date <= week_end_date:
                                    total_posts += 1
                                    if len(recent_posts) < 5:
                                        recent_posts.append(f"- {line.strip()}")
                            except (ValueError, IndexError):
                                continue
        return total_posts, recent_posts
    except Exception as e:
        print(f"Error getting LinkedIn posts: {e}")
        return 0, [f"Error retrieving LinkedIn logs: {e}"]

def get_pending_approvals():
    """Counts pending approval items in AI_Employee_Vault/Needs_Approval/."""
    approvals_dir = "AI_Employee_Vault/Needs_Approval/"
    count = 0
    pending_items = []
    try:
        if os.path.exists(approvals_dir):
            items = [f for f in os.listdir(approvals_dir) if os.path.isfile(os.path.join(approvals_dir, f))]
            count = len(items)
            if count > 0 and len(pending_items) < 5:
                pending_items = [f"- {item}" for item in items[:5]]
        return count, pending_items
    except Exception as e:
        print(f"Error getting pending approvals: {e}")
        return 0, [f"Error retrieving approval data: {e}"]

def get_weekly_income_expense(week_start_date, week_end_date):
    """Gets the weekly income/expense summary by running the accounting manager script."""
    try:
        # We need to run the accounting_manager.py script to get the weekly summary
        # The end_date for the summary should be the end of our reporting week.
        # We need to format it as YYYY-MM-DD for the script.
        end_date_str = week_end_date.strftime('%Y-%m-%d')
        
        # Construct the command to run the accounting script
        command = [
            "python",
            ACCOUNTING_SCRIPT,
            "weekly-summary",
            f"--end-date={end_date_str}"
        ]
        
        # Execute the command
        # We need to capture stdout for the summary
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # The output is expected to be the formatted summary
        summary = result.stdout.strip()
        return summary
    except FileNotFoundError:
        return "Accounting script not found. Please ensure it is installed and in the PATH."
    except subprocess.CalledProcessError as e:
        return f"Error generating accounting summary: {e.stderr.strip()}"
    except Exception as e:
        return f"An unexpected error occurred while fetching accounting summary: {e}"

def get_system_health():
    """Performs a basic system health check."""
    health_status = "OK"
    details = []

    # Check if report and log directories are writable
    try:
        os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
        
        test_report_file = os.path.join(os.path.dirname(REPORT_FILE), ".health_check_report_write_")
        with open(test_report_file, "w") as f: # try to create file
            f.write("test")
        os.remove(test_report_file) # clean up
        
        test_log_file = os.path.join(LOG_DIR, ".health_check_log_write_")
        with open(test_log_file, "w") as f: # try to create file
            f.write("test")
        os.remove(test_log_file) # clean up
        
    except OSError as e:
        health_status = "WARNING"
        details.append(f"Cannot write to output directories ({e}). Check permissions.")

    # Add more checks as needed (e.g., disk space, process status)
    # For now, a basic check is sufficient.
    if not details:
        details.append("Directory permissions check passed.")

    return health_status, details

# --- Report Generation ---
def generate_ceo_briefing(report_date):
    """Generates the full CEO weekly briefing report."""
    ensure_directories()

    # Determine the date range for the report (e.g., previous Monday to Sunday)
    # If report_date is a Monday, it's the start of the week for this report.
    # If report_date is any other day, we find the Monday of that week.
    # For simplicity, let's assume report_date is today and we want last Mon-Sun.
    # Or, if generating for a specific Monday, use that. Let's use current date to find last week.

    # Calculate the start and end of the previous week (Mon-Sun)
    # If today is Monday, today - 7 days is last Monday. If today is Sunday, today - 6 days is this Sunday.
    # Better to define week start and end based on report_date
    
    # Let's aim for the week ending on the Sunday *before* the given report_date
    # If report_date is 2026-03-03 (Tuesday), the week ending is 2026-03-01 (Sunday)
    # If report_date is 2026-03-02 (Monday), the week ending is 2026-02-29 (Sunday)
    
    # Calculate the Sunday of the week containing report_date
    # day_of_week: Monday is 0, Sunday is 6
    day_of_week = report_date.weekday()
    # Sunday is 6. If today is Tuesday (2), Sunday is 4 days away (6-2=4). If today is Monday (0), Sunday is 6 days away (6-0=6).
    days_to_sunday = 6 - day_of_week
    end_of_reporting_week = report_date + timedelta(days=days_to_sunday)
    
    # The week starts 6 days before the end Sunday
    start_of_reporting_week = end_of_reporting_week - timedelta(days=6)
    
    print(f"Generating report for week: {start_of_reporting_week.strftime('%Y-%m-%d')} to {end_of_reporting_week.strftime('%Y-%m-%d')}")

    # --- Gather Data ---
    tasks_completed_count, recent_tasks = get_tasks_completed(start_of_reporting_week, end_of_reporting_week)
    emails_sent_count, recent_emails = get_emails_sent(start_of_reporting_week, end_of_reporting_week)
    linkedin_posts_count, recent_posts = get_linkedin_posts(start_of_reporting_week, end_of_reporting_week)
    pending_approvals_count, pending_items = get_pending_approvals()
    accounting_summary = get_weekly_income_expense(end_of_reporting_week)
    health_status, health_details = get_system_health()

    # --- Compile Report ---
    report_content = []
    report_content.append(f"# CEO Weekly Briefing Report
")
    report_content.append(f"**Period:** {start_of_reporting_week.strftime('%Y-%m-%d')} - {end_of_reporting_week.strftime('%Y-%m-%d')}
")

    report_content.append(f"## Key Metrics Summary
")
    report_content.append(f"*   **Tasks Completed:** {tasks_completed_count}
")
    report_content.append(f"*   **Emails Sent:** {emails_sent_count}
")
    report_content.append(f"*   **LinkedIn Posts:** {linkedin_posts_count}
")
    report_content.append(f"*   **Pending Approvals:** {pending_approvals_count}
")

    report_content.append(f"
## Detailed Sections
")

    # Tasks Completed Details
    report_content.append(f"### Tasks Completed ({tasks_completed_count} total)
")
    if recent_tasks:
        report_content.extend(recent_tasks)
    else:
        report_content.append("- No tasks completed this week.")
    report_content.append("
")

    # Emails Sent Details
    report_content.append(f"### Emails Sent ({emails_sent_count} total)
")
    if recent_emails:
        report_content.extend(recent_emails)
    else:
        report_content.append("- No emails sent this week.")
    report_content.append("
")

    # LinkedIn Posts Details
    report_content.append(f"### LinkedIn Posts ({linkedin_posts_count} total)
")
    if recent_posts:
        report_content.extend(recent_posts)
    else:
        report_content.append("- No LinkedIn posts made this week.")
    report_content.append("
")

    # Pending Approvals Details
    report_content.append(f"### Pending Approvals ({pending_approvals_count} items)
")
    if pending_items:
        report_content.extend(pending_items)
    else:
        report_content.append("- No items pending approval.")
    report_content.append("
")

    # Income/Expense Summary
    report_content.append(f"### Weekly Income/Expense Summary
")
    report_content.append(accounting_summary)
    report_content.append("
")

    # System Health
    report_content.append(f"### System Health ({health_status})
")
    for detail in health_details:
        report_content.append(f"- {detail}")
    report_content.append("
")

    # Write to file
    try:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write('
'.join(report_content))
        print(f"Successfully generated CEO Weekly Briefing: {REPORT_FILE}")
    except Exception as e:
        print(f"Error writing report to {REPORT_FILE}: {e}")

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="CEO Briefing Skill: Generates weekly reports.")
    parser.add_argument("--action", type=str, default="generate-report",
                        choices=["generate-report"],
                        help="Action to perform.")
    # Optional: Specify a date to generate the report for (defaults to today)
    # This is useful for testing or generating reports for past weeks.
    parser.add_argument("--report-date", type=str, help="Date to base the report week on (YYYY-MM-DD). Defaults to today.")
    
    args = parser.parse_args()

    if args.action == "generate-report":
        if args.report_date:
            try:
                report_date = datetime.strptime(args.report_date, '%Y-%m-%d')
            except ValueError:
                print("Error: Invalid --report-date format. Please use YYYY-MM-DD.")
                return
        else:
            report_date = datetime.now()
        
        generate_ceo_briefing(report_date)

if __name__ == "__main__":
    main()
