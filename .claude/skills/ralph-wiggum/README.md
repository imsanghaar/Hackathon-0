# 🎯 Ralph Wiggum Autonomous Loop - Quick Start Guide

## Overview

The **Ralph Wiggum Autonomous Loop** automatically processes tasks from start to finish with built-in safety measures.

| Feature | Description |
|---------|-------------|
| 🧠 **Task Analysis** | AI-powered understanding of task requirements |
| 📋 **Plan Generation** | Creates step-by-step Plan.md |
| ⚡ **Step Execution** | Executes one step at a time |
| ✅ **Result Checking** | Validates each step before continuing |
| 🛑 **Safety Limits** | Max 5 iterations per task |
| 👤 **Human Approval** | Required for risky actions |

---

## 🚀 Quick Start

### Run Autonomous Loop

```bash
# Process all pending tasks
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py --run

# Process specific task
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py --task task_001.md

# Check status
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py --status

# View active loops
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py --active
```

### Automatic Execution

Integrated with main scheduler - runs automatically each cycle:

```bash
# Run scheduler (includes Ralph Wiggum loop)
python scripts/run_ai_employee.py --daemon
```

---

## 📁 File Structure

```
ralph-wiggum/
├── scripts/
│   ├── ralph_wiggum.py        # Main loop script
│   ├── task_analyzer.py       # Task analysis (built-in)
│   ├── plan_generator.py      # Plan generation (built-in)
│   ├── step_executor.py       # Step execution (built-in)
│   └── risk_checker.py        # Risk assessment (built-in)
├── SKILL.md                    # Full documentation
└── README.md                   # This quick start guide
```

---

## 🔄 How It Works

### Task Flow

```
1. Task appears in Needs_Action/
   │
   ↓
2. Analyze Task → task_analysis.json
   │
   ↓
3. Create Plan → Plan.md
   │
   ↓
4. Check Risk → Approval needed?
   │
   ├─→ Yes → Wait for approval
   │
   └─→ No → Continue
        │
        ↓
5. Execute Step 1
   │
   ↓
6. Check Result → Success?
   │
   ├─→ No → Error handler
   │
   └─→ Yes → Next step
        │
        ↓
7. Repeat (max 5 iterations)
   │
   ↓
8. Move to Done/
```

---

## 📋 Plan.md Format

```markdown
# Task Plan: Review Client Notes

**Created:** 2026-03-02 12:00:00
**Status:** In Progress
**Iteration:** 2/5
**Task Type:** analysis
**Complexity:** medium

---

## Steps

- [x] Step 1: Read source material
- [x] Step 2: Analyze key points
- [ ] Step 3: Summarize findings
- [ ] Step 4: Create report
- [ ] Step 5: Save analysis

---

## Execution Log

| Step | Status | Timestamp | Notes |
|------|--------|-----------|-------|
| 1 | ✅ Complete | 12:01:00 | Step completed successfully |
| 2 | ✅ Complete | 12:02:00 | Step completed successfully |
| 3 | ⏳ Pending | - | - |
```

---

## 🛡️ Safety Features

### Risk Levels

| Level | Actions | Approval |
|-------|---------|----------|
| **Low** | Read, analyze, review | ❌ No |
| **Medium** | Create, write, modify | ❌ No (logged) |
| **High** | Delete, send, publish | ✅ Yes |
| **Critical** | API calls, payments | ✅ Yes (mandatory) |

### Iteration Limit

- **Maximum 5 iterations** per task
- Prevents infinite loops
- Tasks exceeding limit are moved to Errors

---

## 📊 CLI Commands

| Command | Description |
|---------|-------------|
| `--run` | Process all pending tasks |
| `--task <file>` | Process specific task |
| `--status` | Show loop status |
| `--active` | Show active loops |
| `--approve <task>` | Approve pending task |
| `--reject <task>` | Reject pending task |

---

## 🔍 Sample Output

### Status Command

```
============================================================
         Ralph Wiggum Loop Status
============================================================

📊 Statistics:
  Pending Tasks: 3
  Active Loops: 1
  Pending Approval: 0
  Completed Today: 5
============================================================
```

### Run Command

```
============================================================
         Ralph Wiggum Autonomous Loop
============================================================

Found 2 pending task(s)

[START] Processing task_001.md
[ANALYZE] task_001.md
[PLAN] Creating plan for task_001.md
[RISK] Assessing risk level
[EXECUTE] Step 1/3: Read source material...
[CHECK] Step 1 complete ✅
[EXECUTE] Step 2/3: Analyze key points...
[CHECK] Step 2 complete ✅
[EXECUTE] Step 3/3: Summarize findings...
[CHECK] Step 3 complete ✅
[DONE] task_001.md moved to Done folder

============================================================
         Summary
============================================================
  Completed: 1
  Pending Approval: 0
  Failed/Max Iterations: 0
============================================================
```

---

## 🔧 Integration with Scheduler

Ralph Wiggum is **automatically integrated** into the main scheduler:

```bash
# Each scheduler cycle runs Ralph Wiggum
python scripts/run_ai_employee.py --daemon
```

**Scheduler Cycle:**
1. Error Recovery - Process retry queue
2. Vault Watcher - Check Inbox
3. Gmail Watcher - Check emails
4. **Ralph Wiggum** - Process pending tasks
5. CEO Briefing - Weekly report (if scheduled)

---

## ⚙️ Configuration

Edit `ralph_wiggum.py` to customize:

```python
# Safety settings
MAX_ITERATIONS = 5           # Maximum steps per task
AUTO_APPROVE_LOW_RISK = True # Auto-approve low risk tasks

# Risk detection
RISK_KEYWORDS = {
    "critical": ["delete", "payment", "api"],
    "high": ["send", "email", "post"],
    "medium": ["create", "modify"],
    "low": ["read", "analyze"]
}
```

---

## 🛠️ Troubleshooting

### Task Stuck in Loop

1. Check iteration count (max 5)
2. Review plan for issues
3. Check error logs

### Approval Required

```bash
# View pending approvals
ls AI_Employee_Vault/Needs_Approval/

# Approve task
python ralph_wiggum.py --approve task_001.md

# Reject task
python ralph_wiggum.py --reject task_001.md
```

### Tasks Not Processing

1. Check scheduler is running
2. Verify task in Needs_Action/
3. Check loop logs: `cat Logs/ralph_loop.log`

---

## 📝 Best Practices

1. **Start simple** - Test with low-risk tasks first
2. **Monitor progress** - Check status regularly
3. **Review plans** - Ensure plans are reasonable
4. **Handle approvals** - Don't block the loop
5. **Check logs** - Review execution logs for issues

---

## 🔗 Related Skills

| Skill | Integration |
|-------|-------------|
| **error-recovery** | Handles execution errors |
| **human-approval** | Manages approval requests |
| **task-planner** | Creates tasks for Ralph |
| **schedular-silvertier** | Runs Ralph in cycles |

---

## 📞 Support

For detailed documentation, see [SKILL.md](./SKILL.md)

**Version:** 1.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System by ISC
