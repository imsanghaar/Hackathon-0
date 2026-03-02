#!/usr/bin/env python3
"""
CEO Weekly Briefing Generator

Generates a comprehensive weekly CEO briefing report at:
AI_Employee_Vault/Reports/CEO_Weekly.md

Includes:
- Tasks Completed
- Emails Sent
- LinkedIn Posts
- Pending Approvals
- Income/Expense Summary
- System Health

Designed for auto-scheduling via schedular-silvertier.
"""

import datetime
import os
import glob
import json

# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = r"E:\ai_employee\Hackathon-0"
REPORTS_DIR = os.path.join(BASE_DIR, "AI_Employee_Vault", "Reports")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
CLAUDE_LOGS_DIR = os.path.join(BASE_DIR, ".claude", "Logs")
VAULT_DIR = os.path.join(BASE_DIR, "AI_Employee_Vault")

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)


# =============================================================================
# Data Collection Functions
# =============================================================================

def get_week_date_range():
    """Get the date range for the current week (Monday to Sunday)."""
    today = datetime.datetime.now()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")


def get_tasks_completed():
    """
    Gather tasks completed from System_Log.md and Done folder.
    Returns a formatted string with task completion info.
    """
    tasks_list = []
    
    # Check System_Log.md for completed tasks
    system_log_path = os.path.join(BASE_DIR, "System_Log.md")
    if os.path.exists(system_log_path):
        with open(system_log_path, 'r', encoding='utf-8') as f:
            log_content = f.readlines()
        
        for line in log_content:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["completed", "done", "finished", "processed"]):
                if "task" in line_lower or "review" in line_lower or "file" in line_lower:
                    tasks_list.append(f"- {line.strip()}")
    
    # Count files in Done folder
    done_dir = os.path.join(VAULT_DIR, "Done")
    if os.path.exists(done_dir):
        done_files = [f for f in os.listdir(done_dir) if f.endswith('.md')]
        if done_files:
            tasks_list.append(f"- **Total files in Done:** {len(done_files)}")
    
    if tasks_list:
        return "\n".join(tasks_list[-20:])  # Last 20 entries
    return "- No tasks completed this week."


def get_emails_sent():
    """
    Gather emails sent from email logs.
    Returns a formatted string with email activity.
    """
    emails_list = []
    
    # Check emails_sent.log
    emails_log_path = os.path.join(CLAUDE_LOGS_DIR, "emails_sent.log")
    if os.path.exists(emails_log_path):
        with open(emails_log_path, 'r', encoding='utf-8') as f:
            emails_content = f.readlines()
        
        for line in emails_content:
            if "sent" in line.lower() or "email" in line.lower():
                emails_list.append(f"- {line.strip()}")
    
    # Check action.log for email actions
    action_log_path = os.path.join(LOGS_DIR, "action.log")
    if os.path.exists(action_log_path):
        with open(action_log_path, 'r', encoding='utf-8') as f:
            action_content = f.readlines()
        
        for line in action_content:
            if "send_email" in line.lower() or "email sent" in line.lower():
                emails_list.append(f"- {line.strip()}")
    
    if emails_list:
        return "\n".join(emails_list[-20:])  # Last 20 entries
    return "- No emails sent this week."


def get_linkedin_posts():
    """
    Gather LinkedIn posts from LinkedIn logs.
    Returns a formatted string with LinkedIn activity.
    """
    posts_list = []
    
    # Check linkedin_posts.log
    linkedin_log_path = os.path.join(CLAUDE_LOGS_DIR, "linkedin_posts.log")
    if os.path.exists(linkedin_log_path):
        with open(linkedin_log_path, 'r', encoding='utf-8') as f:
            linkedin_content = f.readlines()
        
        for line in linkedin_content:
            if "post" in line.lower() or "linkedin" in line.lower():
                posts_list.append(f"- {line.strip()}")
    
    # Check action.log for LinkedIn actions
    action_log_path = os.path.join(LOGS_DIR, "action.log")
    if os.path.exists(action_log_path):
        with open(action_log_path, 'r', encoding='utf-8') as f:
            action_content = f.readlines()
        
        for line in action_content:
            if "linkedin" in line.lower() or "post_linkedin" in line.lower():
                posts_list.append(f"- {line.strip()}")
    
    # Check business.log from MCP server
    business_log_path = os.path.join(BASE_DIR, "vault", "Logs", "business.log")
    if os.path.exists(business_log_path):
        with open(business_log_path, 'r', encoding='utf-8') as f:
            business_content = f.readlines()
        
        for line in business_content:
            if "linkedin" in line.lower():
                posts_list.append(f"- {line.strip()}")
    
    if posts_list:
        return "\n".join(posts_list[-20:])  # Last 20 entries
    return "- No LinkedIn posts this week."


def get_pending_approvals():
    """
    Get list of pending approvals from Needs_Approval folder.
    Returns a formatted string with pending items.
    """
    needs_approval_dir = os.path.join(VAULT_DIR, "Needs_Approval")
    
    if os.path.exists(needs_approval_dir):
        pending_files = [f for f in os.listdir(needs_approval_dir) if os.path.isfile(os.path.join(needs_approval_dir, f))]
        
        if pending_files:
            # Read approval details if available
            approval_details = []
            for file in sorted(pending_files):
                file_path = os.path.join(needs_approval_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(200)  # First 200 chars
                        # Extract approval reason if present
                        for line in content.split('\n'):
                            if 'reason:' in line.lower() or 'action:' in line.lower():
                                approval_details.append(f"- **{file}**: {line.strip()}")
                                break
                        else:
                            approval_details.append(f"- {file}")
                except Exception:
                    approval_details.append(f"- {file}")
            
            return "\n".join(approval_details)
        else:
            return "- No files pending approval."
    else:
        return "- Approval folder not found."


def get_income_expense_summary():
    """
    Gather income/expense data from accounting logs.
    Returns a formatted string with financial summary.
    """
    summary_lines = []
    total_income = 0.0
    total_expense = 0.0
    
    # Check for accounting manager logs
    accounting_log_path = os.path.join(BASE_DIR, "Logs", "accounting.log")
    if os.path.exists(accounting_log_path):
        with open(accounting_log_path, 'r', encoding='utf-8') as f:
            accounting_content = f.readlines()
        
        for line in accounting_content:
            line_lower = line.lower()
            if "income" in line_lower or "revenue" in line_lower or "payment received" in line_lower:
                total_income += extract_amount(line)
                summary_lines.append(f"- {line.strip()}")
            elif "expense" in line_lower or "cost" in line_lower or "payment made" in line_lower:
                total_expense += extract_amount(line)
                summary_lines.append(f"- {line.strip()}")
    
    # Check business.log from MCP server
    business_log_path = os.path.join(BASE_DIR, "vault", "Logs", "business.log")
    if os.path.exists(business_log_path):
        with open(business_log_path, 'r', encoding='utf-8') as f:
            business_content = f.readlines()
        
        for line in business_content:
            line_lower = line.lower()
            if "payment" in line_lower or "invoice" in line_lower or "transaction" in line_lower:
                if "received" in line_lower or "income" in line_lower:
                    total_income += extract_amount(line)
                elif "paid" in line_lower or "expense" in line_lower:
                    total_expense += extract_amount(line)
    
    # Build summary
    if summary_lines:
        summary = "\n".join(summary_lines[-15:])
        summary += f"\n\n**Weekly Totals:**\n"
        summary += f"- Total Income: ${total_income:.2f}\n"
        summary += f"- Total Expenses: ${total_expense:.2f}\n"
        summary += f"- Net: ${total_income - total_expense:.2f}"
        return summary
    
    # If no data, check for any financial files
    financial_data_found = False
    for log_file in glob.glob(os.path.join(LOGS_DIR, "*.log")):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if any(word in content for word in ["payment", "invoice", "income", "expense", "revenue"]):
                    financial_data_found = True
                    break
        except Exception:
            pass
    
    if financial_data_found:
        return "- Financial data exists but not in standard format. Review logs manually."
    
    return "- No income/expense data recorded this week.\n- Configure accounting-manager skill to track finances."


def extract_amount(text):
    """Extract dollar amount from text."""
    import re
    # Match patterns like $100, $1,000.00, 100 USD, etc.
    patterns = [
        r'\$[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*(?:usd|dollars?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group().replace('$', '').replace(',', '').replace('USD', '').replace('dollars', '').strip()
            try:
                return float(amount_str)
            except ValueError:
                pass
    return 0.0


def get_system_health():
    """
    Gather system health metrics.
    Returns a formatted string with system status.
    """
    health_items = []
    
    # Check for running processes / lock files
    lock_file_path = os.path.join(LOGS_DIR, "scheduler.lock")
    if os.path.exists(lock_file_path):
        try:
            with open(lock_file_path, 'r') as f:
                pid = f.read().strip()
            health_items.append(f"- ✅ **Scheduler:** Running (PID: {pid})")
        except Exception:
            health_items.append(f"- ⚠️ **Scheduler:** Lock file exists but unreadable")
    else:
        health_items.append(f"- ⏸️ **Scheduler:** Not running")
    
    # Check log file sizes
    log_files = {
        "Action Log": os.path.join(LOGS_DIR, "action.log"),
        "AI Employee Log": os.path.join(LOGS_DIR, "ai_employee.log"),
        "System Log": os.path.join(BASE_DIR, "System_Log.md"),
    }
    
    for name, path in log_files.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if size_mb > 10:
                health_items.append(f"- ⚠️ **{name}:** Large ({size_mb:.1f} MB) - consider rotation")
            else:
                health_items.append(f"- ✅ **{name}:** OK ({size_mb:.2f} MB)")
        else:
            health_items.append(f"- ❌ **{name}:** Not found")
    
    # Check vault folder counts
    vault_folders = {
        "Inbox": os.path.join(VAULT_DIR, "Inbox"),
        "Needs_Action": os.path.join(VAULT_DIR, "Needs_Action"),
        "Needs_Approval": os.path.join(VAULT_DIR, "Needs_Approval"),
        "Done": os.path.join(VAULT_DIR, "Done"),
    }
    
    for name, path in vault_folders.items():
        if os.path.exists(path):
            count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            if name == "Inbox" and count > 10:
                health_items.append(f"- ⚠️ **{name}:** {count} files (needs attention)")
            elif name == "Needs_Action" and count > 5:
                health_items.append(f"- ⚠️ **{name}:** {count} files (backlog)")
            else:
                health_items.append(f"- ✅ **{name}:** {count} files")
        else:
            health_items.append(f"- ❌ **{name}:** Not found")
    
    # Check MCP server status
    mcp_business_log = os.path.join(BASE_DIR, "vault", "Logs", "business.log")
    if os.path.exists(mcp_business_log):
        try:
            # Check if log was updated in last hour
            mtime = os.path.getmtime(mcp_business_log)
            hours_ago = (datetime.datetime.now().timestamp() - mtime) / 3600
            if hours_ago < 1:
                health_items.append(f"- ✅ **MCP Business Server:** Active")
            else:
                health_items.append(f"- ⏸️ **MCP Business Server:** Idle ({hours_ago:.1f}h since last activity)")
        except Exception:
            health_items.append(f"- ❓ **MCP Business Server:** Status unknown")
    
    # Check for errors in recent logs
    error_count = 0
    for log_file in [os.path.join(LOGS_DIR, "action.log"), os.path.join(LOGS_DIR, "ai_employee.log")]:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]  # Last 100 lines
                    for line in lines:
                        if "error" in line.lower() or "failed" in line.lower() or "exception" in line.lower():
                            error_count += 1
            except Exception:
                pass
    
    if error_count > 10:
        health_items.append(f"- ⚠️ **Recent Errors:** {error_count} errors detected - review logs")
    elif error_count > 0:
        health_items.append(f"- ℹ️ **Recent Errors:** {error_count} minor errors logged")
    else:
        health_items.append(f"- ✅ **Recent Errors:** None")
    
    return "\n".join(health_items)


# =============================================================================
# Report Generation
# =============================================================================

def generate_ceo_briefing():
    """
    Generate the weekly CEO briefing report.
    """
    week_start, week_end, report_date = get_week_date_range()
    report_path = os.path.join(REPORTS_DIR, "CEO_Weekly.md")
    
    # Gather all data
    tasks_completed = get_tasks_completed()
    emails_sent = get_emails_sent()
    linkedin_posts = get_linkedin_posts()
    pending_approvals = get_pending_approvals()
    income_expense_summary = get_income_expense_summary()
    system_health = get_system_health()
    
    # Construct the report content
    report_content = f"""# CEO Weekly Briefing

**Report Generated:** {report_date}  
**Week:** {week_start} to {week_end}

---

## 📋 Tasks Completed

{tasks_completed}

---

## 📧 Emails Sent

{emails_sent}

---

## 💼 LinkedIn Posts

{linkedin_posts}

---

## ⏳ Pending Approvals

{pending_approvals}

---

## 💰 Income/Expense Summary

{income_expense_summary}

---

## 🏥 System Health

{system_health}

---

*This report was automatically generated by the CEO Briefing Skill.*
"""
    
    # Write the report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Use encode errors='replace' for Windows console compatibility
    print("[OK] CEO Weekly Briefing generated successfully!")
    print(f"Report location: {report_path}")
    print(f"Report period: {week_start} to {week_end}")
    
    return report_path


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    generate_ceo_briefing()
