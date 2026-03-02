# 🛡️ Error Recovery Skill - Quick Start Guide

## Overview

The **Error Recovery Skill** provides automatic error handling and recovery for failed tasks in the AI Employee system.

| Feature | Description |
|---------|-------------|
| 📝 **Error Logging** | Detailed logs with timestamp, error type, and stack trace |
| 📁 **File Quarantine** | Failed files moved to Errors folder |
| 🔄 **Automatic Retry** | One retry attempt after 5 minutes |
| 📊 **Statistics** | Track error counts and recovery success |

---

## 🚀 Quick Start

### Check Error Status

```bash
# View error statistics
python .claude/skills/error-recovery/scripts/error_recovery.py --status
```

### Process Retry Queue

```bash
# Check and process files due for retry
python .claude/skills/error-recovery/scripts/error_recovery.py --check
```

### View Errors

```bash
# View recent error log (last 50 entries)
python .claude/skills/error-recovery/scripts/error_recovery.py --log

# View last 100 entries
python .claude/skills/error-recovery/scripts/error_recovery.py --log --limit 100

# View retry queue
python .claude/skills/error-recovery/scripts/error_recovery.py --queue
```

### Recover Files

```bash
# Recover a specific file from Errors folder
python .claude/skills/error-recovery/scripts/error_recovery.py --recover task_001.md

# Clean up old errors (older than 7 days)
python .claude/skills/error-recovery/scripts/error_recovery.py --cleanup

# Clear all errors
python .claude/skills/error-recovery/scripts/error_recovery.py --clear
```

---

## 📁 File Structure

```
error-recovery/
├── scripts/
│   ├── error_recovery.py      # CLI interface
│   └── error_handler.py       # Core error handling logic
├── SKILL.md                    # Full documentation
└── README.md                   # This quick start guide

AI_Employee_Vault/Errors/       # Quarantined failed files
Logs/
├── errors.log                  # Error log file
└── retry_queue.json            # Pending retry queue
```

---

## 🔧 Integration with Your Skills

### Basic Usage

```python
from .claude.skills.error-recovery.scripts.error_handler import ErrorHandler

# Initialize handler
errors = ErrorHandler()

try:
    # Your task logic
    process_file(filename)
except Exception as e:
    # Handle error automatically
    result = errors.handle_error(
        filename=filename,
        error=e,
        source="your-skill-name",
        retry=True  # Enable auto-retry
    )
    print(f"Error handled: {result}")
```

### In Task Planner

```python
from error_handler import ErrorHandler
errors = ErrorHandler()

def process_file(filename):
    try:
        # Processing logic
        with open(filename) as f:
            content = f.read()
        # ... process content
    except Exception as e:
        errors.handle_error(filename, e, "task-planner", retry=True)
```

### In Gmail Watcher

```python
from error_handler import ErrorHandler
errors = ErrorHandler()

def check_emails():
    try:
        # Email checking logic
        pass
    except Exception as e:
        errors.handle_error("gmail", e, "gmail-watcher", retry=True)
```

---

## ⚙️ How It Works

### Error Flow

```
1. Error Occurs
   │
   ├─→ 2. Log to errors.log
   │
   ├─→ 3. Move file to Errors/
   │
   └─→ 4. Queue for retry (if enabled)
        │
        └─→ After 5 minutes: Move back to Inbox
```

### Error Categories

| Category | Examples | Retry? |
|----------|----------|--------|
| **Network** | Connection timeout, HTTP errors | ✅ Yes |
| **File** | File not found, path errors | ✅ Yes |
| **Permission** | Access denied | ❌ No |
| **Parsing** | JSON/YAML errors | ❌ No |
| **Validation** | Invalid data | ❌ No |

---

## 📋 CLI Commands

| Command | Description |
|---------|-------------|
| `--check` | Process retry queue |
| `--recover <file>` | Recover specific file |
| `--log` | View error log |
| `--log --limit N` | View last N log entries |
| `--queue` | View retry queue |
| `--cleanup` | Remove old errors |
| `--cleanup --days N` | Remove errors older than N days |
| `--status` | Show statistics |
| `--clear` | Clear all errors |

---

## 📊 Sample Output

### Status Command

```
============================================================
         Error Recovery Status
============================================================

📊 Statistics:
  Total Errors Logged: 15
  Errors Today: 3
  Pending Retries: 2
  Files in Errors Folder: 8

============================================================
```

### Check Command

```
============================================================
         Error Recovery - Processing Retry Queue
============================================================

Results:
  Total Pending: 2
  Retried: 1
  Successful: 1
  Failed: 0
  Max Attempts Reached: 0
============================================================
```

### Queue Command

```
============================================================
         Retry Queue
============================================================

Pending Retries: 2

1. task_001.md
   Source: task-planner
   Category: network
   Attempts: 1/2
   Retry At: 2026-03-02 12:35:00
   Created: 2026-03-02 12:30:00

2. task_002.md
   Source: gmail-watcher
   Category: file
   Attempts: 1/2
   Retry At: 2026-03-02 12:40:00
   Created: 2026-03-02 12:35:00

============================================================
```

---

## ⚙️ Configuration

Edit `error_handler.py` to customize:

```python
# Retry settings
RETRY_DELAY_MINUTES = 5          # Wait time before retry
MAX_RETRY_ATTEMPTS = 2           # Maximum retry attempts

# File paths
ERRORS_LOG = "Logs/errors.log"
RETRY_QUEUE = "Logs/retry_queue.json"
ERRORS_FOLDER = "AI_Employee_Vault/Errors"

# Auto-cleanup
AUTO_CLEANUP_DAYS = 7            # Remove old errors after N days
```

---

## 🔍 Error Log Format

```
[2026-03-02 12:00:00] [ERROR] [task-planner] File: task_001.md
  Type: FileNotFoundError
  Category: file
  Message: File not found: /path/to/file.md
  Action: Moved to Errors folder
  Stack Trace:
    File "task_planner.py", line 45, in process_file
      with open(filename) as f:
  ============================================================
```

---

## 🛠️ Troubleshooting

### Errors Not Being Logged

1. Check Logs folder exists: `ls Logs/`
2. Verify write permissions
3. Check error_handler.py is imported correctly

### Retry Not Working

1. Check queue: `python error_recovery.py --queue`
2. Verify 5 minutes have passed
3. Check max_attempts not exceeded

### Files Not Moving to Errors

1. Check Errors folder exists: `ls AI_Employee_Vault/Errors/`
2. Verify write permissions
3. Check source file still exists

---

## 📝 Best Practices

1. **Always catch exceptions** - Use error_handler in all skills
2. **Enable retry for transient errors** - Network issues, rate limits
3. **Disable retry for permanent errors** - Invalid data, missing files
4. **Review Errors folder weekly** - Check quarantined files
5. **Monitor error log** - Set up alerts for critical errors
6. **Clean up old errors** - Run `--cleanup` weekly

---

## 🔗 Integration with Main Scheduler

Error recovery is **automatically integrated** into the main scheduler:

```bash
# Run scheduler (includes error recovery check)
python scripts/run_ai_employee.py --daemon

# Single cycle
python scripts/run_ai_employee.py --once
```

Each scheduler cycle:
1. Processes retry queue
2. Moves due files back to Inbox
3. Logs retry results

---

## 📞 Support

For detailed documentation, see [SKILL.md](./SKILL.md)

**Version:** 1.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System by ISC
