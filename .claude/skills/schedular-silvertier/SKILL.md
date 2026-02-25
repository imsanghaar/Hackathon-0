---
name: "schedular-silvertier"
description: "Run vault-watcher and task-planner in a loop with configurable interval (default 6 minutes). Supports --daemon, --once, --status modes. Logs to logs/ai_employee.log with 4MB rotation. Prevents duplicate instances with lock files."
---

# Scheduler SilverTier Skill

## When to Use

- User says "Start scheduler" or "Run schedular-silvertier"
- User wants automated periodic execution of vault-watcher and task-planner
- User needs continuous monitoring with daemon mode
- User wants to check scheduler status

## Procedure

1. **Check for existing instance (lock file)**
   - Prevent duplicate scheduler runs
   - Use `Logs/scheduler.lock` file

2. **Based on mode, execute:**
   - `--daemon`: Run vault-watcher and task-planner in continuous loop
   - `--once`: Single execution of both components
   - `--status`: Show active tasks and inbox count

3. **Log all actions to logs/ai_employee.log**
   - Scheduler start/stop
   - Each vault-watcher cycle
   - Each task-planner execution
   - Errors and warnings

4. **Rotate logs when exceeding 4MB**
   - Archive old logs with timestamp
   - Create fresh log file

## Output Format

**Daemon Mode Start:**
```
╔══════════════════════════════════════════════════════════╗
║           🤖 AI Employee Scheduler - Silver Tier          ║
╠══════════════════════════════════════════════════════════╣
║  Mode: Daemon (continuous)                               ║
║  Interval: 6 minutes (360 seconds)                       ║
║  Log File: logs/ai_employee.log                          ║
║  Max Log Size: 4 MB                                      ║
╚══════════════════════════════════════════════════════════╝

[2026-02-24 23:00:00] Scheduler started in daemon mode
[2026-02-24 23:00:01] Running vault-watcher cycle...
[2026-02-24 23:00:05] Running task-planner cycle...
[2026-02-24 23:06:00] Next cycle in 360 seconds...
```

**Once Mode:**
```
╔══════════════════════════════════════════════════════════╗
║           🤖 AI Employee Scheduler - Silver Tier          ║
╠══════════════════════════════════════════════════════════╣
║  Mode: Once (single execution)                           ║
║  Log File: logs/ai_employee.log                          ║
╚══════════════════════════════════════════════════════════╝

[2026-02-24 23:00:00] Running single scheduler cycle...
[2026-02-24 23:00:01] Vault-watcher: 0 new files detected
[2026-02-24 23:00:02] Task-planner: 0 files processed
[2026-02-24 23:00:02] Scheduler cycle complete
```

**Status Mode:**
```
╔══════════════════════════════════════════════════════════╗
║           📊 AI Employee Scheduler Status                 ║
╠══════════════════════════════════════════════════════════╣
║  Scheduler Status: Running (PID: 12345)                  ║
║  Inbox Files: 3                                          ║
║  Pending Tasks: 5                                        ║
║  Last Cycle: 2026-02-24 22:54:00                         ║
║  Next Cycle: 2026-02-24 23:00:00                         ║
║  Log Size: 1.2 MB                                        ║
╚══════════════════════════════════════════════════════════╝
```

**Action Log Entry:**
```log
[2026-02-24 23:00:00] SCHEDULER: Started in daemon mode
[2026-02-24 23:00:01] SCHEDULER: Running vault-watcher cycle
[2026-02-24 23:00:05] SCHEDULER: Running task-planner cycle
[2026-02-24 23:00:05] SCHEDULER: Cycle complete - 0 inbox, 0 processed
[2026-02-24 23:06:00] SCHEDULER: Next cycle in 360 seconds
```

## Important Rules

- **Lock file enforcement:** Only one scheduler instance at a time
- **Log rotation:** Rotate at 4MB, keep archived logs
- **Graceful shutdown:** Handle Ctrl+C in daemon mode
- **Error recovery:** Continue running even if cycle fails
- **Default interval:** 6 minutes between cycles

## File Paths

- **Scheduler Script:** `scripts/run_ai_employee.py`
- **Log File:** `logs/ai_employee.log`
- **Lock File:** `Logs/scheduler.lock`
- **Vault Watcher:** `scripts/watch_inbox.py`
- **Task Planner:** `scripts/task_planner.py`

## Running the Scheduler

**Daemon mode (continuous):**
```bash
python scripts/run_ai_employee.py --daemon
```

**Single execution:**
```bash
python scripts/run_ai_employee.py --once
```

**Check status:**
```bash
python scripts/run_ai_employee.py --status
```

**Custom interval:**
```bash
python scripts/run_ai_employee.py --daemon --interval 300
```

**Force start (ignore lock):**
```bash
python scripts/run_ai_employee.py --daemon --force
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--interval` | 360s | Time between cycles in daemon mode |
| `--log-max-size` | 4MB | Maximum log file size before rotation |
| `--lock-file` | Logs/scheduler.lock | Lock file path |

## Integration with Other Skills

**With Vault Watcher:**
```python
# Scheduler calls vault-watcher each cycle
from watch_inbox import main as run_watcher
run_watcher()
```

**With Task Planner:**
```python
# Scheduler calls task-planner each cycle
from task_planner import TaskPlanner
planner = TaskPlanner()
planner.process_inbox()
```

## Troubleshooting

- **Scheduler won't start:** Check for stale lock file (`rm Logs/scheduler.lock`)
- **Log file too large:** Check log rotation settings
- **Duplicate instances:** Lock file should prevent this
- **Cycle fails:** Check `logs/ai_employee.log` for errors
