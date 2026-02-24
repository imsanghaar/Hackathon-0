# Agent Skill: Process Tasks

## Trigger Phrase
When the user says: **"Process Tasks"**

## Workflow

1. **Open the Needs_Action folder**
   - List all task files (`.md` files)

2. **Read each task file**
   - Parse the YAML frontmatter (type, status, source, filename, created_at)
   - Read the task content and checklist items

3. **Understand the task**
   - Identify what action is required based on the task content

4. **Mark as completed**
   - Change `status: pending` to `status: completed`
   - Check off all checklist items (`- [x]`)

5. **Move to Done folder**
   - Move the updated task file from `Needs_Action/` to `DOne/`

6. **Update Dashboard.md**
   - Add task entry under "Completed Tasks" section
   - Remove from "Pending Tasks" section (if present)

7. **Log to System_Log.md**
   - Append a short entry in the Activity Log table describing what was completed

## Rules
- Always actually edit the files (never simulate)
- Process all tasks in Needs_Action folder
- Maintain file structure and formatting
