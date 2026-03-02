---
name: error-recovery
description: Automatic error handling and recovery system. Logs errors, moves failed files to Errors folder, and retries failed tasks after 5 minutes.
---

# Error Recovery Skill

## Overview

This skill provides automatic error handling and recovery for failed tasks in the AI Employee system. When any task fails, it:

1. **Logs the error** to `Logs/errors.log` with full details
2. **Moves failed files** to `AI_Employee_Vault/Errors` for review
3. **Retries once** after 5 minutes automatically

## Features

| Feature | Description |
|---------|-------------|
| **Error Logging** | Detailed error logs with timestamp, file, error type, and stack trace |
| **File Quarantine** | Failed files moved to Errors folder to prevent repeated failures |
| **Automatic Retry** | One retry attempt after 5 minutes for transient errors |
| **Error Categories** | Automatic categorization (network, file, permission, parsing, unknown) |
| **Recovery Queue** | Tracks files pending retry |
| **Integration** | Works with all other skills via simple API |

## Installation

No additional dependencies required. Uses Python standard library.

## Usage

### Manual Error Recovery

```bash
# Run error recovery check (processes retry queue)
python .claude/skills/error-recovery/scripts/error_recovery.py --check

# Manually recover a specific file
python .claude/skills/error-recovery/scripts/error_recovery.py --recover <filename>

# View error log
python .claude/skills/error-recovery/scripts/error_recovery.py --log

# View retry queue
python .claude/skills/error-recovery/scripts/error_recovery.py --queue

# Clear old errors (older than 7 days)
python .claude/skills/error-recovery/scripts/error_recovery.py --cleanup
```

### Programmatic Usage

```python
from error_handler import ErrorHandler

# Initialize handler
handler = ErrorHandler()

# Log an error and queue for retry
handler.handle_error(
    filename="task_file.md",
    error=Exception("Something went wrong"),
    source="task-planner",
    retry=True
)

# Check and process retry queue
handler.process_retry_queue()
```

## Integration with Other Skills

### In Your Skill's Error Handling

```python
from .claude.skills.error-recovery.scripts.error_handler import ErrorHandler

error_handler = ErrorHandler()

try:
    # Your task logic
    process_file(filename)
except Exception as e:
    error_handler.handle_error(
        filename=filename,
        error=e,
        source="your-skill-name",
        retry=True  # Enable auto-retry
    )
```

### Integration with Main Scheduler

The error recovery is automatically called in the main scheduler cycle:

```bash
# Main scheduler runs error recovery check each cycle
python scripts/run_ai_employee.py --daemon
```

## File Structure

```
error-recovery/
├── scripts/
│   ├── error_recovery.py      # Main CLI script
│   └── error_handler.py       # Core error handling logic
├── SKILL.md                    # This documentation
└── README.md                   # Quick start guide

AI_Employee_Vault/Errors/       # Quarantined failed files
Logs/errors.log                 # Error log file
Logs/retry_queue.json           # Pending retry queue
```

## Error Log Format

```
[2026-03-02 12:00:00] [ERROR] [task-planner] File: task_001.md
  Type: FileNotFoundError
  Message: File not found: /path/to/file.md
  Action: Moved to Errors, Retry scheduled in 5 minutes
  Stack Trace:
    File "task_planner.py", line 45, in process_file
      with open(filename) as f:
  ---
```

## Retry Queue Format

```json
{
  "pending_retries": [
    {
      "filename": "task_001.md",
      "source": "task-planner",
      "error_type": "FileNotFoundError",
      "retry_time": "2026-03-02T12:05:00",
      "attempts": 1,
      "max_attempts": 2
    }
  ]
}
```

## Error Categories

| Category | Detection | Action |
|----------|-----------|--------|
| **Network** | Connection errors, timeouts | Retry with backoff |
| **File** | File not found, access denied | Move to Errors |
| **Permission** | Access denied, unauthorized | Log and alert |
| **Parsing** | JSON/YAML parse errors | Move to Errors |
| **Unknown** | All other errors | Log and retry |

## Configuration

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

## CLI Options

| Option | Description |
|--------|-------------|
| `--check` | Check retry queue and process due items |
| `--recover <file>` | Manually recover a specific file |
| `--log` | Display recent error log entries |
| `--queue` | Show pending retry queue |
| `--cleanup` | Remove errors older than 7 days |
| `--clear` | Clear all errors and queue |

## Example Output

```
╔══════════════════════════════════════════════════════════╗
║           Error Recovery Status                           ║
╠══════════════════════════════════════════════════════════╣
║  Pending Retries: 2                                      ║
║  Errors Today: 5                                         ║
║  Errors Folder: 12 files                                 ║
╚══════════════════════════════════════════════════════════╝

[OK] Processing retry queue...
[RETRY] task_001.md -> Moving back to Inbox
[SUCCESS] task_001.md retry successful
[FAILED] task_002.md retry failed (max attempts reached)
```

## Best Practices

1. **Always catch exceptions** - Use error_handler in all skills
2. **Enable retry for transient errors** - Network issues, rate limits
3. **Disable retry for permanent errors** - Invalid data, missing files
4. **Review Errors folder weekly** - Check quarantined files
5. **Monitor error log** - Set up alerts for critical errors
6. **Clean up old errors** - Run --cleanup weekly

## Troubleshooting

### Errors Not Being Logged

1. Check Logs folder exists and is writable
2. Verify error_handler.py is imported correctly
3. Check file permissions on errors.log

### Retry Not Working

1. Check retry queue: `--queue`
2. Verify 5 minutes have passed since error
3. Check max_attempts not exceeded

### Files Not Moving to Errors

1. Check AI_Employee_Vault/Errors folder exists
2. Verify write permissions
3. Check source file still exists

## API Reference

### ErrorHandler Class

```python
class ErrorHandler:
    def __init__(self, base_dir=None)
    def handle_error(self, filename, error, source, retry=True)
    def process_retry_queue(self)
    def log_error(self, filename, error, source, action)
    def move_to_errors(self, filename)
    def queue_retry(self, filename, source, error_type)
    def get_error_stats(self)
    def cleanup_old_errors(self, days=7)
```

## Integration Examples

### With Task Planner

```python
from error_handler import ErrorHandler
errors = ErrorHandler()

def process_file(filename):
    try:
        # Processing logic
        pass
    except Exception as e:
        errors.handle_error(filename, e, "task-planner", retry=True)
```

### With Gmail Watcher

```python
from error_handler import ErrorHandler
errors = ErrorHandler()

def check_email():
    try:
        # Email checking logic
        pass
    except Exception as e:
        errors.handle_error("gmail", e, "gmail-watcher", retry=True)
```

### With LinkedIn Auto-Post

```python
from error_handler import ErrorHandler
errors = ErrorHandler()

def post_to_linkedin(content):
    try:
        # Posting logic
        pass
    except Exception as e:
        errors.handle_error("linkedin", e, "linkedin-auto-post", retry=False)
```

---

**Version:** 1.0
**Last Updated:** March 2, 2026
**Author:** AI Employee System by ISC
