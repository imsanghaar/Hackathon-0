---
name: ceo-briefing
description: Generates a weekly CEO briefing report at AI_Employee_Vault/Reports/CEO_Weekly.md with tasks, emails, LinkedIn posts, approvals, finances, and system health. Includes auto-scheduler.
---

# CEO Briefing Skill

## Overview

This skill generates a comprehensive weekly CEO briefing report that consolidates all key operational metrics and system health indicators. The report is saved to `AI_Employee_Vault/Reports/CEO_Weekly.md`.

## Features

| Section | Description |
|---------|-------------|
| **Tasks Completed** | Aggregated from System_Log.md and Done folder |
| **Emails Sent** | From email logs and action logs |
| **LinkedIn Posts** | From LinkedIn post logs and MCP business logs |
| **Pending Approvals** | Current files in Needs_Approval folder |
| **Income/Expense Summary** | Financial data from accounting logs |
| **System Health** | Scheduler status, log sizes, folder counts, error detection |

## Installation

No additional dependencies required. The skill uses Python standard library.

## Usage

### Generate Report Manually

```bash
python .claude/skills/ceo-briefing/scripts/generate_ceo_briefing.py
```

### Schedule Weekly Auto-Run

```bash
# Install default schedule (Every Monday at 9:00 AM)
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --install

# Custom schedule (Every Friday at 5:00 PM)
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --install --day 4 --hour 17

# Run immediately
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --run

# Check status
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --status

# Uninstall schedule
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --uninstall
```

### Scheduler Options

| Option | Description | Default |
|--------|-------------|---------|
| `--install` | Install weekly schedule | - |
| `--run` | Run briefing immediately | - |
| `--status` | Show schedule status | - |
| `--uninstall` | Remove schedule | - |
| `--day N` | Day of week (0=Monday, 6=Sunday) | 0 (Monday) |
| `--hour N` | Hour in 24h format | 9 |
| `--minute N` | Minute | 0 |

## Auto-Scheduling Setup

### Option 1: Internal Scheduler (Recommended)

The schedule script saves configuration to `.claude/skills/ceo-briefing/schedule.json`. Integrate with `schedular-silvertier`:

```bash
# In your schedular-silvertier configuration, add ceo-briefing to weekly rotation
# The scheduler will check schedule.json and run when due
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task: "CEO Weekly Briefing"
3. Trigger: Weekly on Monday at 09:00
4. Action: Start a program
   - Program: `python`
   - Arguments: `E:\ai_employee\Hackathon-0\.claude\skills\ceo-briefing\scripts\generate_ceo_briefing.py`
   - Start in: `E:\ai_employee\Hackathon-0`

### Option 3: Linux/macOS Cron

```bash
# Edit crontab
crontab -e

# Add entry for every Monday at 9 AM
0 9 * * 1 python3 /mnt/e/ai_employee/Hackathon-0/.claude/skills/ceo-briefing/scripts/generate_ceo_briefing.py
```

## Report Output

The generated report follows this structure:

```markdown
# CEO Weekly Briefing

**Report Generated:** 2026-03-02
**Week:** 2026-02-24 to 2026-03-02

---

## 📋 Tasks Completed
- Completed review of task_001.md
- Processed file: client_request.md
...

## 📧 Emails Sent
- Email sent to client@example.com
...

## 💼 LinkedIn Posts
- LinkedIn post published: "Excited to announce..."
...

## ⏳ Pending Approvals
- approval_001.md: Delete test records
...

## 💰 Income/Expense Summary
- Payment received: $5000
- Total Income: $5000.00
- Total Expenses: $0.00
- Net: $5000.00

## 🏥 System Health
- ✅ Scheduler: Running (PID: 12345)
- ✅ Action Log: OK (0.5 MB)
- ✅ Inbox: 2 files
...
```

## Log Files

| Log | Location |
|-----|----------|
| Scheduler Log | `Logs/ceo_briefing_scheduler.log` |
| Schedule Config | `.claude/skills/ceo-briefing/schedule.json` |
| Generated Reports | `AI_Employee_Vault/Reports/CEO_Weekly.md` |

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **gmail-send** | Reads email logs for "Emails Sent" section |
| **linkedin-auto-post** | Reads LinkedIn logs for "LinkedIn Posts" section |
| **human-approval** | Reads Needs_Approval folder for "Pending Approvals" |
| **accounting-manager** | Reads accounting logs for "Income/Expense Summary" |
| **schedular-silvertier** | Can trigger weekly execution |

## Customization

### Add New Report Sections

Edit `generate_ceo_briefing.py` and add a new getter function:

```python
def get_new_section():
    """Get data for new section."""
    # Your implementation
    return "- New section data"
```

Then add it to the report content:

```python
report_content = f"""
...

## New Section

{get_new_section()}

...
"""
```

### Change Report Location

Modify `REPORTS_DIR` in the script:

```python
REPORTS_DIR = r"E:\ai_employee\Hackathon-0\AI_Employee_Vault\Reports"
```

## Troubleshooting

### Report Not Generated

1. Check Python is in PATH: `python --version`
2. Verify script exists: `ls .claude/skills/ceo-briefing/scripts/`
3. Check permissions on Reports folder

### Missing Data in Sections

- **Tasks Completed:** Ensure System_Log.md exists and has entries
- **Emails Sent:** Check `.claude/Logs/emails_sent.log` exists
- **LinkedIn Posts:** Verify `linkedin-auto-post` skill logs to correct file
- **Income/Expense:** Configure `accounting-manager` skill

### Scheduler Not Running

1. Check schedule config: `python schedule_ceo_briefing.py --status`
2. Review scheduler log: `cat Logs/ceo_briefing_scheduler.log`
3. Verify system scheduler (Task Scheduler/cron) is configured

## Example Output

```
╔══════════════════════════════════════════════════════════╗
║           📅 CEO Briefing Schedule Installed              ║
╠══════════════════════════════════════════════════════════╣
║  Frequency: Weekly                                        ║
║  Day: Monday                                              ║
║  Time: 09:00                                              ║
║  Log: Logs/ceo_briefing_scheduler.log                     ║
╚══════════════════════════════════════════════════════════╝
```

## Best Practices

1. **Review reports weekly** - Check generated reports every Monday
2. **Archive old reports** - Move old reports to archive folder monthly
3. **Monitor log size** - Rotate logs if they exceed 10MB
4. **Update financial tracking** - Configure accounting-manager for accurate finances

## Files

```
.ceo-briefing/
├── scripts/
│   ├── generate_ceo_briefing.py    # Main report generator
│   └── schedule_ceo_briefing.py    # Scheduler management
├── schedule.json                    # Schedule configuration
└── SKILL.md                         # This documentation
```

---

**Version:** 2.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System
