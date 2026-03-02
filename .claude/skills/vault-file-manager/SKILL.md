---
name: "vault-file-manager"
description: "Manage task workflow by moving files between Inbox, Needs_Action, and Done folders."
---

# Vault File Manager Skill

## When to Use
- Move files between vault folders
- Organize task files
- Complete task workflow

## Usage
```bash
python .claude/skills/vault-file-manager/scripts/move_task.py --file "filename.md" --to "Done"
```

## Folders
- `Inbox/` - New incoming files
- `Needs_Action/` - Pending tasks
- `Done/` - Completed tasks

## Output Format
- SUCCESS: `Moved {filename} to {folder}`
- ERROR: `Failed: {error message}`

## Important Rules
- Validate file exists before moving
- Create destination folder if needed
- Log all file movements
