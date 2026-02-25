---
name: "vault-watcher"
description: "Continuously monitor AI_Employee_Vault/Inbox folder for new .md files. When detected, log to logs/action.log and trigger AI Processing workflow. Uses file tracking to avoid processing duplicates. Runs every 10-30 seconds."
---

# Vault Watcher Skill

## When to Use

- User says "Start vault watcher" or "Run vault-watcher"
- User wants to monitor AI_Employee_Vault/Inbox for new files
- User needs automated AI processing of incoming markdown files
- User requests continuous file monitoring workflow

## Procedure

1. **Start the watcher script** located at `scripts/watch_inbox.py`
2. **The watcher will:**
   - Monitor `AI_Employee_Vault/Inbox/` folder continuously
   - Check for new `.md` files every 10-30 seconds (randomized interval)
   - Track processed files in `Logs/processed_files.txt` to avoid duplicates
   - Log each detection to `logs/action.log`
   - Trigger AI Processing workflow for new files

3. **For each new .md file detected:**
   - Log detection timestamp and filename to `logs/action.log`
   - Add filename to processed tracker
   - Trigger the AI Processing workflow (same as `run_ai_employee.py --once`)

4. **AI Processing workflow will:**
   - Read the new .md file from Inbox
   - Process it according to its content/type
   - Move to appropriate folder (Needs_Action, Done, etc.)

## Output Format

**Watcher Start Message:**
```
👁️ Vault Watcher Started
├─ Monitoring: AI_Employee_Vault/Inbox/
├─ Check Interval: 10-30 seconds (randomized)
├─ Processed Tracker: Logs/processed_files.txt
└─ Action Log: logs/action.log
```

**File Detection Log Entry (in logs/action.log):**
```
[2026-02-24 14:30:45] DETECTED: new_file.md - Triggering AI Processing
```

**Completion Summary (when stopped):**
```
✅ Vault Watcher Stopped
├─ Total files processed: X
├─ Total detections logged: Y
└─ Uptime: Z minutes
```

## Important Rules

- **Never process the same file twice** - Use `Logs/processed_files.txt` tracker
- **Randomize check interval** - Between 10-30 seconds to avoid patterns
- **Log every detection** - All detections go to `logs/action.log`
- **Graceful shutdown** - Handle Ctrl+C and save state before exit
- **Error resilience** - Continue running even if individual operations fail
- **Lightweight operation** - Minimal resource usage, no heavy dependencies

## File Paths

- **Inbox folder:** `AI_Employee_Vault/Inbox/`
- **Processed tracker:** `Logs/processed_files.txt`
- **Action log:** `logs/action.log`
- **Watcher script:** `scripts/watch_inbox.py`
- **Base directory:** `E:\ai_employee\[Bronze_Tier](Silver_Tier)\`

## Running the Watcher

**Start watcher:**
```bash
python scripts/watch_inbox.py
```

**Start in background (Linux/Mac):**
```bash
python scripts/watch_inbox.py &
```

**Start in background (Windows):**
```bash
start /B python scripts/watch_inbox.py
```

**Stop watcher:**
- Press `Ctrl+C` in terminal
- Or send SIGTERM to process

## Integration with AI Employee

The watcher triggers the same workflow as:
```bash
python ai_employee.py --once
```

This ensures consistency with the main AI Employee system.

## Troubleshooting

- **Watcher not detecting files:** Check that Inbox folder path is correct
- **Duplicate processing:** Verify `Logs/processed_files.txt` is being updated
- **No logs appearing:** Check `logs/action.log` permissions
- **High CPU usage:** Ensure sleep interval is working (10-30 seconds)
- **Script crashes:** Check `Logs/watcher_errors.log` for error details

## Example Action Log

```log
# Vault Watcher Action Log

[2026-02-24 14:30:45] WATCHER_STARTED - Monitoring AI_Employee_Vault/Inbox/
[2026-02-24 14:31:12] DETECTED: meeting_notes.md - Triggering AI Processing
[2026-02-24 14:31:12] PROCESSED: meeting_notes.md - Added to tracker
[2026-02-24 14:32:05] DETECTED: task_request.md - Triggering AI Processing
[2026-02-24 14:32:05] PROCESSED: task_request.md - Added to tracker
[2026-02-24 14:35:00] WATCHER_STOPPED - Processed 2 files, Uptime: 4 minutes
```
