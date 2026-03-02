---
name: "process-tasks"
description: "Process all pending tasks from the Needs_Action folder. Reads each task file, marks it as completed, moves it to Done folder, and updates Dashboard.md and System_Log.md. Use when user says 'Process Tasks' or asks to complete pending tasks."
---

# Process Tasks Skill

## When to Use

- User says "Process Tasks"
- User asks to complete pending tasks
- User wants to move tasks from Needs_Action to Done
- User requests task processing workflow

## Procedure

1. **Open the Needs_Action folder** and list all `.md` task files
2. **Read each task file** to understand its content and frontmatter
3. **For each task file:**
   - Change `status: pending` to `status: completed` in the frontmatter
   - Write the updated content back to the file
   - Move the file from `Needs_Action/` to `Done/` folder
4. **Update Dashboard.md:**
   - Read current dashboard content
   - Remove processed tasks from "Pending Tasks" section
   - Add completed tasks to "Completed Tasks" section with timestamp
   - Write updated dashboard back
5. **Update System_Log.md:**
   - Append a new entry documenting what was completed
   - Include: date, action ("Process Tasks"), number of tasks completed
6. **Report completion** to user with summary

## Output Format

**Completion Summary**

```
✅ Processed X task(s):

Completed:
- [x] task_filename_1.md
- [x] task_filename_2.md
- [x] task_filename_3.md

Files moved to: Done/
Dashboard updated: Yes
System Log updated: Yes
```

## Important Rules

- **Always actually edit the files** - Do not simulate or pretend
- **Move files physically** - Use file system operations to move from Needs_Action to Done
- **Update both Dashboard and System_Log** - This is required for tracking
- **Preserve task content** - Only change status field, keep everything else intact
- **Log important actions** - Record completion in System_Log.md
- **Confirm before destructive actions** - If user asks to delete instead of move, confirm first
- **Handle errors gracefully** - If a file can't be moved, report the error but continue with others

## File Paths

- **Needs_Action folder:** `E:\ai_employee\[Bronze_Tier](Silver_Tier)\Needs_Action\`
- **Done folder:** `E:\ai_employee\[Bronze_Tier](Silver_Tier)\Done\`
- **Dashboard:** `E:\ai_employee\[Bronze_Tier](Silver_Tier)\Dashboard.md`
- **System Log:** `E:\ai_employee\[Bronze_Tier](Silver_Tier)\System_Log.md`

## Example Task Frontmatter

```yaml
---
type: file_review
status: pending
priority: medium
created_at: 2026-02-24 12:00:00
related_files: ["document.pdf"]
---
```

**After processing:**
```yaml
---
type: file_review
status: completed
priority: medium
created_at: 2026-02-24 12:00:00
related_files: ["document.pdf"]
---
```

## Troubleshooting

- **If Needs_Action is empty:** Report "No pending tasks to process"
- **If file move fails:** Log error to `Logs/watcher_errors.log` and continue
- **If Dashboard doesn't exist:** Create it with proper structure
- **If System_Log doesn't exist:** Create it with Activity Log table
