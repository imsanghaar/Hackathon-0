# 📊 CEO Briefing Skill - Quick Start Guide

## Overview

The **CEO Briefing Skill** automatically generates comprehensive weekly reports covering all key business operations:

| Section | Description |
|---------|-------------|
| 📋 **Tasks Completed** | All processed tasks from System_Log.md and Done folder |
| 📧 **Emails Sent** | Email activity from gmail-send skill logs |
| 💼 **LinkedIn Posts** | Social media activity from linkedin-auto-post |
| ⏳ **Pending Approvals** | Items awaiting approval in Needs_Approval |
| 💰 **Income/Expense** | Financial summary from accounting-manager |
| 🏥 **System Health** | Scheduler status, log sizes, error detection |

---

## 🚀 Quick Start

### 1. Generate Report Manually

```bash
# Navigate to project directory
cd E:\ai_employee\Hackathon-0

# Generate CEO weekly briefing
python .claude/skills/ceo-briefing/scripts/generate_ceo_briefing.py
```

**Output:**
```
[OK] CEO Weekly Briefing generated successfully!
Report location: E:\ai_employee\Hackathon-0/AI_Employee_Vault/Reports/CEO_Weekly.md
Report period: 2026-03-02 to 2026-03-08
```

### 2. Schedule Automatic Weekly Reports

```bash
# Install default schedule (Every Monday at 9:00 AM)
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --install

# Custom schedule (Every Friday at 5:00 PM)
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --install --day 4 --hour 17

# Check schedule status
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --status

# Run briefing immediately (on-demand)
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --run

# Uninstall schedule
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --uninstall
```

### 3. Auto-Run via Main Scheduler (Recommended)

The CEO Briefing is **automatically integrated** into the main AI Employee scheduler:

```bash
# Run scheduler in daemon mode (continuous)
python scripts/run_ai_employee.py --daemon

# Run single cycle (checks schedule, runs if due)
python scripts/run_ai_employee.py --once

# Check scheduler status
python scripts/run_ai_employee.py --status
```

**How it works:**
- Every scheduler cycle checks if today is the scheduled day
- If scheduled day matches (default: Monday), generates the report
- No duplicate reports - runs once per week automatically

---

## 📁 File Structure

```
.claude/skills/ceo-briefing/
├── scripts/
│   ├── generate_ceo_briefing.py    # Main report generator
│   └── schedule_ceo_briefing.py    # Scheduler management
├── schedule.json                    # Schedule configuration (created on install)
├── SKILL.md                         # Full documentation
└── README.md                        # This quick start guide

AI_Employee_Vault/Reports/
└── CEO_Weekly.md                    # Generated weekly report
```

---

## ⚙️ Scheduler Options

| Option | Description | Default |
|--------|-------------|---------|
| `--install` | Install weekly schedule | - |
| `--run` | Run briefing immediately | - |
| `--status` | Show schedule status | - |
| `--uninstall` | Remove schedule | - |
| `--day N` | Day of week (0=Monday, 6=Sunday) | 0 (Monday) |
| `--hour N` | Hour in 24h format (0-23) | 9 |
| `--minute N` | Minute (0-59) | 0 |

---

## 📋 Sample Report

```markdown
# CEO Weekly Briefing

**Report Generated:** 2026-03-02
**Week:** 2026-03-02 to 2026-03-08

---

## 📋 Tasks Completed

- | 2026-02-24 | Process Tasks | Completed 1 task(s) via AI Agent |
- | 2026-02-24 | Process Tasks | Completed 3 task(s) via Interactive CLI |

---

## 📧 Emails Sent

- [2026-02-25 12:59:11] To: client@example.com | Subject: Project Update

---

## 💼 LinkedIn Posts

- [2026-02-26 10:00:00] LinkedIn post published: "Excited to announce..."

---

## ⏳ Pending Approvals

- approval_20260224_232523.txt: Delete test records

---

## 💰 Income/Expense Summary

- Payment received: $5000
- Total Income: $5000.00
- Total Expenses: $0.00
- Net: $5000.00

---

## 🏥 System Health

- ✅ Scheduler: Running (PID: 12345)
- ✅ Action Log: OK (0.5 MB)
- ✅ Inbox: 2 files
- ✅ Needs_Action: 1 files
- ⚠️ Recent Errors: 0 errors
```

---

## 🔧 Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **gmail-send** | Reads email logs for "Emails Sent" section |
| **linkedin-auto-post** | Reads LinkedIn logs for "LinkedIn Posts" section |
| **human-approval** | Reads Needs_Approval folder for "Pending Approvals" |
| **accounting-manager** | Reads accounting logs for "Income/Expense Summary" |
| **run_ai_employee.py** | Auto-triggers weekly via main scheduler |

---

## 🖥️ System Scheduler Setup (Optional)

For **additional reliability**, add to your system scheduler:

### Windows Task Scheduler

1. Open **Task Scheduler**
2. Create Basic Task: **"CEO Weekly Briefing"**
3. Trigger: **Weekly on Monday at 09:00**
4. Action: **Start a program**
   - Program: `python`
   - Arguments: `E:\ai_employee\Hackathon-0\.claude\skills\ceo-briefing\scripts\generate_ceo_briefing.py`
   - Start in: `E:\ai_employee\Hackathon-0`

### Linux/macOS Cron

```bash
# Edit crontab
crontab -e

# Add entry for every Monday at 9 AM
0 9 * * 1 python3 /mnt/e/ai_employee/Hackathon-0/.claude/skills/ceo-briefing/scripts/generate_ceo_briefing.py
```

---

## 📊 Log Files

| Log | Location |
|-----|----------|
| Scheduler Log | `Logs/ceo_briefing_scheduler.log` |
| Schedule Config | `.claude/skills/ceo-briefing/schedule.json` |
| Generated Reports | `AI_Employee_Vault/Reports/CEO_Weekly.md` |
| Main Scheduler Log | `Logs/ai_employee.log` |

---

## 🛠️ Troubleshooting

### Report Not Generated

1. **Check Python is in PATH:**
   ```bash
   python --version
   ```

2. **Verify script exists:**
   ```bash
   ls .claude/skills/ceo-briefing/scripts/
   ```

3. **Check permissions on Reports folder:**
   ```bash
   ls -la AI_Employee_Vault/Reports/
   ```

### Missing Data in Sections

| Section | Check |
|---------|-------|
| **Tasks Completed** | Ensure `System_Log.md` exists and has entries |
| **Emails Sent** | Check `.claude/Logs/emails_sent.log` exists |
| **LinkedIn Posts** | Verify `linkedin-auto-post` skill logs correctly |
| **Income/Expense** | Configure `accounting-manager` skill |

### Scheduler Not Running

1. **Check schedule config:**
   ```bash
   python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --status
   ```

2. **Review scheduler log:**
   ```bash
   cat Logs/ceo_briefing_scheduler.log
   ```

3. **Verify main scheduler is running:**
   ```bash
   python scripts/run_ai_employee.py --status
   ```

---

## 📝 Best Practices

1. **Review reports weekly** - Check generated reports every Monday morning
2. **Archive old reports** - Move old reports to archive folder monthly
3. **Monitor log size** - Rotate logs if they exceed 10MB
4. **Update financial tracking** - Configure accounting-manager for accurate finances
5. **Clear pending approvals** - Review and process items in Needs_Approval

---

## 🎯 Example Commands

```bash
# Generate report for testing
python .claude/skills/ceo-briefing/scripts/generate_ceo_briefing.py

# Install Friday 5 PM schedule
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --install --day 4 --hour 17

# Run briefing on-demand (ignore schedule)
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --run

# Check if schedule is active
python .claude/skills/ceo-briefing/scripts/schedule_ceo_briefing.py --status

# Run main scheduler once (will trigger CEO briefing if scheduled)
python scripts/run_ai_employee.py --once

# Start continuous scheduler (auto-runs CEO briefing weekly)
python scripts/run_ai_employee.py --daemon
```

---

## 📞 Support

For detailed documentation, see [SKILL.md](./SKILL.md)

**Version:** 2.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System by ISC
