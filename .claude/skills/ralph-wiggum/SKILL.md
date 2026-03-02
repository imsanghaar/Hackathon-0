---
name: ralph-wiggum
description: Autonomous task execution loop with iterative planning. Analyzes tasks, creates plans, executes steps, checks results, and repeats until completion. Includes safety controls (max 5 iterations, human approval for risky tasks).
---

# Ralph Wiggum Autonomous Loop

## Overview

An autonomous task execution system that implements an iterative approach to task completion:

1. **Analyze Task** - Parse and understand task requirements
2. **Create Plan.md** - Generate step-by-step execution plan
3. **Execute First Step** - Begin task execution
4. **Check Result** - Verify step completion
5. **Continue Next Step** - Proceed through plan
6. **Repeat Until Completed** - Iterate until done
7. **Move Task to Done** - Archive completed task

## Safety Features

| Feature | Description | Default |
|---------|-------------|---------|
| **Max Iterations** | Maximum loop iterations per task | 5 |
| **Human Approval** | Required for risky actions | Auto-detected |
| **State Persistence** | Recovery from interruptions | Enabled |
| **Risk Detection** | Keywords triggering approval | Configurable |

## Installation

No additional dependencies required. Uses Python standard library.

## Usage

### Run Autonomous Loop

```bash
# Process all tasks in Inbox
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py run

# Process specific task
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py run --task my_task.md

# Legacy flag syntax
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py --run
```

### Check Status

```bash
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py status
```

**Output:**
```
============================================================
         Ralph Wiggum Autonomous Loop Status
============================================================

Active Tasks: 2
  - client_request.md (Step 3, Iteration 2)
  - data_cleanup.md (Step 1, Iteration 1)

Pending Approvals: 1
  - ralph_20260302_140000: delete_old_records.md

Completed Tasks: 5
  - email_campaign.md (2026-03-02 13:45:00)
  - report_generation.md (2026-03-02 12:30:00)

Last Run: 2026-03-02 14:00:00
Max Iterations: 5
============================================================
```

### Approve/Risk Actions

```bash
# Approve pending action
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py approve ralph_20260302_140000

# Reject pending action
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py reject ralph_20260302_140000
```

## Risk Detection

Tasks are flagged as risky and require approval if they contain:

### Action Keywords
- `delete`, `remove`, `drop`, `destroy`, `permanent`
- `payment`, `transfer`, `send money`, `wire`
- `password`, `secret`, `credential`, `api key`
- `approve`, `authorize`, `confirm`

### Priority Levels
- `high`, `urgent`, `critical`

## Plan Structure

Generated plans follow this format:

```markdown
---
type: autonomous_plan
status: active
created_at: 2026-03-02T14:00:00
source_task: my_task.md
task_type: client_request
priority: normal
is_risky: false
max_iterations: 5
---

# Autonomous Plan: my_task.md

## Task Analysis

- **Source File:** my_task.md
- **Type:** client_request
- **Priority:** normal
- **Risk Level:** Normal
- **Analyzed At:** 2026-03-02 14:00:00

## Risk Assessment

**Approval Required:** No

## Execution Steps

### Step 1: Review Task Content
- **Status:** pending
- **Result:** 
- **Notes:** 

### Step 2: Identify Required Actions
- **Status:** pending
- **Result:** 
- **Notes:** 

### Step 3: Execute Primary Action
- **Status:** pending
- **Result:** 
- **Notes:** 

### Step 4: Verify Results
- **Status:** pending
- **Result:** 
- **Notes:** 

### Step 5: Finalize and Archive
- **Status:** pending
- **Result:** 
- **Notes:** 

## Execution Log

| Iteration | Step | Status | Timestamp |
|-----------|------|--------|-----------|
| 0 | Plan Created | Complete | 2026-03-02 14:00:00 |

## Completion Status

- [ ] All steps executed
- [ ] Results verified
- [ ] Task moved to Done
```

## Integration with Scheduler

### schedular-silvertier Integration

Add Ralph Wiggum to your scheduler rotation:

```bash
# In schedular-silvertier configuration
# Add ralph_wiggum.py to the execution cycle

python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py run
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task: "Ralph Wiggum Autonomous Loop"
3. Trigger: Daily at 09:00
4. Action: Start a program
   - Program: `python`
   - Arguments: `.claude/skills/ralph-wiggum/scripts/ralph_wiggum.py run`
   - Start in: `E:\ai_employee\Hackathon-0`

### Linux/macOS Cron

```bash
# Run every hour
0 * * * * python3 /path/to/ralph_wiggum.py run
```

## File Structure

```
ralph-wiggum/
├── scripts/
│   └── ralph_wiggum.py        # Main autonomous loop
├── plans/                      # Generated plans
├── state.json                  # Execution state
└── SKILL.md                    # This documentation

Logs/
├── ralph_loop.log             # Loop iteration log
├── ralph_errors.log           # Error log
└── action.log                 # Action log (shared)

AI_Employee_Vault/
├── Inbox/                     # Input tasks
├── Needs_Action/              # Active plans
├── Needs_Approval/            # Pending approvals
└── Done/                      # Completed tasks
```

## State Management

The skill maintains state in `state.json`:

```json
{
  "active_tasks": [
    {
      "filename": "task.md",
      "path": "AI_Employee_Vault/Inbox/task.md",
      "plan": "plans/Plan_task_20260302_140000.md",
      "current_step": 3,
      "iteration": 2,
      "started_at": "2026-03-02T14:00:00"
    }
  ],
  "completed_tasks": [...],
  "pending_approvals": [...],
  "current_iteration": 2,
  "last_run": "2026-03-02T14:00:00"
}
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Ralph Wiggum Loop                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Analyze Task                                             │
│     - Parse frontmatter                                      │
│     - Extract actions                                        │
│     - Assess risk                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Create Plan.md                                           │
│     - Generate steps                                         │
│     - Set max iterations                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │   Is Risky?   │   │  Not Risky    │
            │      Yes      │   │      No       │
            └───────┬───────┘   └───────┬───────┘
                    │                   │
                    ▼                   │
            ┌───────────────┐           │
            │ Request       │           │
            │ Approval      │           │
            └───────┬───────┘           │
                    │                   │
                    ▼                   │
            ┌───────────────┐           │
            │   Wait for    │           │
            │   Human       │           │
            └───────┬───────┘           │
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3-6. Execute Loop (Max 5 iterations)                        │
│     For each iteration:                                      │
│     - Execute current step                                   │
│     - Check result                                           │
│     - If risky step → Request approval                       │
│     - Move to next step                                      │
│     - If all steps done → Complete                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Move to Done                                             │
│     - Move task file                                         │
│     - Move plan file                                         │
│     - Update state                                           │
└─────────────────────────────────────────────────────────────┘
```

## Log Files

### Loop Log (Logs/ralph_loop.log)
```
[2026-03-02 14:00:00] [INFO] ==================================================
[2026-03-02 14:00:00] [INFO] Starting Ralph Wiggum Autonomous Loop
[2026-03-02 14:00:00] [INFO] ==================================================
[2026-03-02 14:00:01] [INFO] Processing task: client_request.md
[2026-03-02 14:00:02] [INFO] Plan created: Plan_client_request_20260302_140000.md
[2026-03-02 14:00:03] [INFO] Executing step 1: Review task content...
[2026-03-02 14:00:04] [INFO] Step 1 completed successfully
```

### Error Log (Logs/ralph_errors.log)
```
[2026-03-02 14:00:05] ERROR: Failed to execute step 3: Permission denied
```

## Troubleshooting

### Task Not Processing

1. Check task is in `AI_Employee_Vault/Inbox/`
2. Verify file is `.md` format
3. Check `ralph_loop.log` for errors

### Approval Stuck

1. Check `AI_Employee_Vault/Needs_Approval/` for pending requests
2. Approve or reject: `python ralph_wiggum.py approve/reject <id>`

### Loop Not Completing

1. Check iteration count (max 5)
2. Review plan for blocked steps
3. Check error log for failures

### State Corruption

1. Delete `state.json` to reset
2. Active tasks will be re-detected from Inbox

## Best Practices

1. **Review plans** - Check generated plans before approval
2. **Monitor logs** - Check `ralph_loop.log` regularly
3. **Clear approvals** - Process pending approvals daily
4. **Archive completed** - Move old plans from Done monthly

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Max Iterations | `MAX_ITERATIONS` in script | 5 |
| Approval Keywords | `APPROVAL_REQUIRED_KEYWORDS` | See list above |
| State File | `state.json` in skill dir | Auto |
| Plans Directory | `plans/` in skill dir | Auto |

---

**Version:** 1.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System
