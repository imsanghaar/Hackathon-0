# Prompts History

All prompts given since the beginning of this session.

---

## Prompt 1

```
You are a Senior AI Systems Engineer.

We are building a AI Employee that runs locally using a vault structured vault system.
This system must be clean, modular,  and production-style (but beginner friendly).

Your job is now to set up the project structure.

Create these folders if they do not exist:
- Inbox
- Needs_Action
- DOne
- Logs
- Plans

Create these files with useful starter content:

1) Dashboard.md:
Section:
   - Pending Tasks
   - Completed Tasks
   - System Notes

2) Company_Handbook.md:
Include Rules:
   - Always log important actions
   - Never take destructive  actions without confirmation
   - Move completed tasks to  Done
   - Keep task files structures
   - If unsure, Ask for clarification

3) System_Log.md:
Add a title and a section called "Activity Log".

Do not describe. Actually Create these folders and files.
```

---

## Prompt 2

```
Now we are adding the first Bronze Tier Watcher.

Create a Python script named file_watcher.py.

Purpose:
This script monitors the "Inbox" folder.
Whenever a new file appears, it creates a task in "Needs_Action".

Task File Format (Markdown):

---
type: file_review
status: pending
souce: Inbox
filename: <original filename>
created_at: <timestamp>
---

# Task: Review File:

A new file was added to the Inbox.
- [] Review the file
- [] Decide what action is needed

Technical Requirements:
- Use Python
- Check folder every  5 seconds in loop
- Avoide duplicate task creation for the same file
- Add clear comments  for begineers
```

---

## Prompt 3

```
Also create a requirements.txt if any library is needed. Otherwise say no external dependencies required.
```

---

## Prompt 4

```
Now define an Agent Skill behaviour for this AI Employee.

Whenever I say: "Process Tasks"

You must follow this workflow:
1. Open the Needs_Action folder.
2. Read each task file.
3. Understand the task from its content
4. Mark its status as completed inside the file 
5. Move the file to the Done folder.
6. Update Dashboard.md:
   - Add the task under "Completed Tasks"
   - Remove it from "Pending Tasks"
7. Append a short entry to System_Log.md describing what was completed.

This behaviour should be remembered and followed everytime  I Say "Process Tasks". 
Do not simulate - actually Edit the files.
```

---

## Prompt 5

```
Document this in Company_Handbook.md
```

---

## Prompt 6

```
process tasks
```

---

## Prompt 7

```
We are upgrading the task system to be more structured and professional.

Create a reusable task template file at:
Plans/task_template.md

Template Format:

---
type: general_task
status: pending
priority: medium
created_at: <timestamp>
related_files: []
---

# Task Title

## Description
(Explain the task clearly)

# Checklist
- [] Step 1
- [] Step 2
- [] Step 3

## NOtes
(Add any reasoning or context here0

Now update file_watcher.py so that when it creates a task, it follows this improved structure istead of old one.
Keep the task specific to reviewing the new file found  in Inbox.
```

---

## Prompt 8

```
Save the prompt in prompts.md
```

---

## Prompt 9

```
Upgrade file_watcher.py to include proper Error Handling:

Requirements:
- If Inbox Folder does not exist, create it automatically 
- If Needs_Action folder does not exits, create it
- Wrap the main loop in try/except so the script never crashes.
- If an Error occurs, write a short message into Logs/watcher_errors.log with error and timestamp
- Keep the script beginner friendly with comments explaining error handling
```

---

## Prompt 10

```
Create a Python script called log_manager.py

Purpose:
Prevent log files from growing forever.

Behaviour:
- Check System_Log.mdand Logs/watcher_errors.logs
- If any file is larger that 1MB:
    - Rename it with a timestamp (example: System_Log_2026-01-29.md)
    - Start with a fresh empty log file with the original name

Make the script simple and well commented.
No Externel dependencies
```

---

## Prompt 11

```
We are preparing for Silver Tier reasoning Abilities.

Create an Agent Skill behavior:

Whenever I say "Make a Plan for tasks"

You must:
1. Read all the files in Needs_Action
2. Analyze what type of tasks are pending
3. Create a new file inside the Plans named:
   Plan_<timestamp>.md

The Plan file should include:
- Summary of pending tasks
- Suggested order of execution
- Any risks or unclear items
- A short Startegy paragraph.

This is a Planning document only. Do not complete tasks yet.
```

---

## Prompt 12

```
Now save all the prompts in prompt.md and also write  readme.md in root folder in which explain:
1. What it is?
2. What is the tech stack?
3. How does it work?
4. What are its features?
5. What can it do after upgrade?

At last add my intro:
Imam Sanghaar Chandio (prompt Engineer, Web developer) Developer of this Local AI System .
At the starting Include the name of the project (Hackathon 0 - Bronze tier). Its description is:
Bronze Tier: Foundation (Minimum Viable Deliverable)
Estimated time: 8-12 hours
Obsidian vault with Dashboard.md and Company_Handbook.md
One working Watcher script (Gmail OR file system monitoring)
Claude Code successfully reading from and writing to the vault
Basic folder structure: /Inbox, /Needs_Action, /Done
All AI functionality should be implemented as Agent Skills

add this as well. At the end before developer intro tell that the Bronze tier of hackthon zero is completed with today's (Date, Day, time)
```

---
