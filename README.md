# 🤖 AI Employee System - Bronze Tier

> **By Imam Sanghaar Chandio** | Hackathon 0 - Foundation Layer  
> A Local AI Employee System that monitors folders, creates tasks, and manages workflows automatically.

[![Status](https://img.shields.io/badge/status-complete-brightgreen)](https://github.com/imsanghaar/Hackathon-0)
[![Tier](https://img.shields.io/badge/tier-bronze-orange)](https://github.com/imsanghaar/Hackathon-0)
[![Python](https://img.shields.io/badge/python-3.x-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/imsanghaar/Hackathon-0/blob/main/LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Features](#-features)
- [Folder Structure](#-folder-structure)
- [Agent Skills](#-agent-skills)
- [CLI Usage](#-cli-usage)
- [Demo Tasks](#-demo-tasks)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **AI Employee System** is a local automation tool that acts as an intelligent assistant for managing file-based workflows. It monitors folders, automatically creates tasks when new files arrive, and integrates with AI agents (Claude, Gemini, Qwen) to process those tasks.

### Key Capabilities

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI EMPLOYEE SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  📥 MONITOR    →    📝 CREATE    →    🤖 PROCESS    →    ✅ COMPLETE   │
│  Inbox files       Tasks auto        AI Agent handles     Move to Done  │
│  every 5s          in Needs_Action   files & updates      & update logs │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI EMPLOYEE SYSTEM                                │
│                              Bronze Tier                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │   Inbox/     │────▶│ Needs_Action/│────▶│    Done/     │                │
│  │  (New Files) │     │  (Pending)   │     │  (Completed) │                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│         │                    │                    │                         │
│         ▼                    ▼                    ▼                         │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │                    File Watcher                               │         │
│  │              (Monitors every 5 seconds)                       │         │
│  └──────────────────────────────────────────────────────────────┘         │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │                  Interactive CLI                              │         │
│  │         (Menu-driven interface with real-time clock)          │         │
│  └──────────────────────────────────────────────────────────────┘         │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │              AI Agent Integration                             │         │
│  │         (Claude / Gemini / Qwen - External CLI)               │         │
│  └──────────────────────────────────────────────────────────────┘         │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────────────────────────────────────────────────────┐         │
│  │              Dashboard.md + System_Log.md                     │         │
│  │                  (Auto-updated status)                        │         │
│  └──────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW SEQUENCE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  USER          CLI          FILE WATCHER       AI AGENT        VAULT
   │             │                │                │               │
   │─Run CLI────▶│                │                │               │
   │             │─Start watcher─▶│                │               │
   │             │                │                │               │
   │             │◀─New file──────│                │               │
   │             │  detected      │                │               │
   │             │                │                │               │
   │             │─Create task───▶│                │               │
   │             │  in Needs_/    │                │               │
   │             │                │                │               │
   │─Press 3────▶│                │                │               │
   │             │─Show workflow─▶│                │               │
   │             │  instructions  │                │               │
   │             │                │                │               │
   │─Open AI────▶│                │                │◀─"Process     │
   │  Terminal   │                │                │  Tasks"       │
   │             │                │                │               │
   │             │                │                │─Read tasks───▶│
   │             │                │                │               │
   │             │                │                │─Mark complete▶│
   │             │                │                │               │
   │             │                │                │─Move to Done─▶│
   │             │                │                │               │
   │             │                │                │─Update logs──▶│
   │             │                │                │               │
   │─Press Enter▶│                │                │               │
   │             │─Refresh data──▶│                │               │
   │             │                │                │               │
   │◀─Updated───▶│                │                │               │
   │  Dashboard  │                │                │               │
   │             │                │                │               │
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   New File      │
                    │  (Dropped in    │
                    │    Inbox/)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  File Watcher   │
                    │  (Detects in    │
                    │    5 seconds)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Create Task    │
                    │  File with YAML │
                    │  Frontmatter    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Needs_Action/  │
                    │  (Task waits    │
                    │   for process)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  User presses   │
                    │  [3] in CLI     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  AI Agent       │
                    │  (External CLI) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
     │   Mark      │ │   Move to   │ │  Update     │
     │  Complete   │ │   Done/     │ │  Dashboard  │
     └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │   System Log    │
                    │    Updated      │
                    └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/imsanghaar/Hackathon-0.git
cd Hackathon-0

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the interactive CLI
py ai_employee.py
```

### First Run

```
┌══════════════════════════════════════════════════════┐
│     🤖 AI Employee System | By ISC | Bronze Tier     │
│              📅 2026-02-24 17:15:42                  │
└══════════════════════════════════════════════════════┘

📊 Statistics
┌─────────────────────────────────┐
│ 📥 Inbox Files         4        │
│ ⏳ Pending Tasks       0        │
│ ✅ Completed Tasks     5        │
│ 📋 Plans               1        │
└─────────────────────────────────┘

🎯 Main Menu
┌────────────────────────────────────────────────────┐
│ [1] 📥 View Inbox    View files in Inbox           │
│ [2] ⏳ View Tasks    View pending tasks            │
│ [3] ▶️ Process Tasks Process all pending tasks     │
│ [4] 📋 Create Plan   Generate task plan            │
│ [5] 📊 Dashboard     View full dashboard           │
│ [6] 📝 System Log    View activity logs            │
│ [7] 🔄 Refresh       Reload all data               │
│ [q] 🚪 Quit          Exit the application          │
│                                                    │
│ 🔄 Auto-refresh active (every 3s)                  │
│ 👁️ File watcher running                            │
└────────────────────────────────────────────────────┘

Enter your choice [1/2/3/4/5/6/7/q] (7):
```

---

## 🔄 How It Works

### 1. File Monitoring

```
┌────────────────────────────────────────────────────────┐
│                  FILE WATCHER                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Interval: Every 5 seconds                             │
│  Target: Inbox/ folder                                 │
│  Action: Create task file in Needs_Action/             │
│                                                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│  │  Check   │───▶│  Detect  │───▶│  Create  │        │
│  │  Inbox   │    │  New     │    │  Task    │        │
│  │          │    │  File    │    │  File    │        │
│  └──────────┘    └──────────┘    └──────────┘        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2. Task Creation

When a new file is detected:

```yaml
# Generated Task File (task_example.txt.md)
---
type: file_review
status: pending
priority: medium
created_at: 2026-02-24 12:00:00
related_files: ["example.txt"]
---

# Task: Review File - example.txt

## Description
A new file was added to the Inbox and requires review.

## Checklist
- [ ] Open and review the file content
- [ ] Identify the file type and purpose
- [ ] Decide what action is needed

## Notes
- Source: Inbox folder
- Original filename: example.txt
```

### 3. Task Processing

```
┌────────────────────────────────────────────────────────┐
│               TASK PROCESSING WORKFLOW                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Step 1: User presses [3] in CLI                       │
│          ↓                                             │
│  Step 2: Professional dialog appears                   │
│          ↓                                             │
│  Step 3: User opens AI agent (Claude/Gemini/Qwen)      │
│          ↓                                             │
│  Step 4: User says "Process Tasks"                     │
│          ↓                                             │
│  Step 5: AI Agent executes:                            │
│            • Reads Needs_Action/                       │
│            • Marks status: completed                   │
│            • Moves files to Done/                      │
│            • Updates Dashboard.md                      │
│            • Updates System_Log.md                     │
│          ↓                                             │
│  Step 6: User returns to CLI, presses Enter            │
│          ↓                                             │
│  Step 7: CLI refreshes, shows updated counts           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **File Monitoring** | Watches Inbox/ every 5 seconds | ✅ |
| **Auto Task Creation** | Creates structured task files with YAML frontmatter | ✅ |
| **Duplicate Prevention** | Tracks processed files to avoid duplicates | ✅ |
| **Error Handling** | Graceful failure with error logging | ✅ |
| **Log Rotation** | Prevents log files from growing too large | ✅ |

### Interactive CLI Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Beautiful UI** | Colors, animations, smooth transitions | ✅ |
| **Real-Time Clock** | Digital clock updates every iteration | ✅ |
| **Live Dashboard** | Real-time statistics display | ✅ |
| **Auto Refresh** | Background data refresh every 3 seconds | ✅ |
| **Scrollable Tasks** | U/D navigation for long task lists | ✅ |
| **Professional Workflow** | External AI agent integration | ✅ |

### Agent Skills

| Skill | Trigger | Action | Location |
|-------|---------|--------|----------|
| **Process Tasks** | "Process Tasks" | Completes tasks, updates Dashboard & Log | `.claude/skills/process-tasks/` |
| **Make a Plan** | "Make a Plan for tasks" | Creates strategic planning document | `.claude/skills/make-plan-for-tasks/` |

---

## 📁 Folder Structure

```
Hackathon-0/
│
├── .claude/
│   └── skills/                    # AI Agent Skills
│       ├── process-tasks/
│       │   └── SKILL.md           # Process Tasks skill definition
│       └── make-plan-for-tasks/
│           └── SKILL.md           # Make a Plan skill definition
│
├── Inbox/                         # 📥 Drop new files here
│   ├── client_meeting_notes.txt
│   ├── invoice_2026_001.pdf
│   └── team_feedback.md
│
├── Needs_Action/                  # ⏳ Pending task files (auto-created)
│   └── .gitkeep
│
├── Done/                          # ✅ Completed tasks (auto-moved)
│   ├── task_client_meeting_notes.txt.md
│   └── task_invoice_2026_001.pdf.md
│
├── Logs/                          # 📝 System logs
│   ├── processed_files.txt        # Tracks processed files
│   └── watcher_errors.log         # Error log for file watcher
│
├── Plans/                         # 📋 Strategic plans
│   ├── Agent_Skill_Make_Plan.md
│   └── Plan_2026-02-24_15-30-00.md
│
├── ai_employee.py                 # 🎮 Main interactive CLI
├── file_watcher.py                # 👁️ File system monitor
├── log_manager.py                 # 🔄 Log rotation script
├── requirements.txt               # 📦 Python dependencies
├── README.md                      # 📖 This file
├── Dashboard.md                   # 📊 Task overview
├── Company_Handbook.md            # 📜 Rules & guidelines
└── System_Log.md                  # 📝 Activity log
```

---

## 🤖 Agent Skills

### What Are Agent Skills?

Agent Skills are documented behaviors that tell AI agents (Claude Code, Gemini CLI, Qwen Code) how to interact with the vault system.

### Skill Structure

```
┌────────────────────────────────────────────────────────┐
│                  SKILL.md FORMAT                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────┐         │
│  │ YAML Frontmatter                         │         │
│  ├──────────────────────────────────────────┤         │
│  │ name: "skill-name"                       │         │
│  │ description: "What it does"              │         │
│  └──────────────────────────────────────────┘         │
│                                                        │
│  ┌──────────────────────────────────────────┐         │
│  │ Markdown Body                            │         │
│  ├──────────────────────────────────────────┤         │
│  │ • When to Use                            │         │
│  │ • Procedure (step-by-step)               │         │
│  │ • Output Format                          │         │
│  │ • Important Rules                        │         │
│  │ • File Paths                             │         │
│  │ • Troubleshooting                        │         │
│  └──────────────────────────────────────────┘         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Available Skills

#### 1. Process Tasks

**Location:** `.claude/skills/process-tasks/SKILL.md`

**Trigger:** `"Process Tasks"`

**What It Does:**
- Reads all task files in `Needs_Action/`
- Changes `status: pending` to `status: completed`
- Moves files to `Done/`
- Updates `Dashboard.md`
- Appends entry to `System_Log.md`

#### 2. Make a Plan for Tasks

**Location:** `.claude/skills/make-plan-for-tasks/SKILL.md`

**Trigger:** `"Make a Plan for tasks"`

**What It Does:**
- Analyzes all pending tasks
- Creates strategic plan document in `Plans/`
- Includes prioritized execution order
- Identifies risks and unclear items
- Provides strategy recommendations

---

## 💻 CLI Usage

### Running the CLI

```bash
# Interactive mode (default)
py ai_employee.py

# Live dashboard mode (real-time monitoring)
py ai_employee.py --dashboard

# File watcher only (background mode)
py ai_employee.py --watch
```

### Menu Options

```
┌────────────────────────────────────────────────────────┐
│                    MAIN MENU                           │
├───────┬──────────────────┬─────────────────────────────┤
│  Key  │     Action       │      Description            │
├───────┼──────────────────┼─────────────────────────────┤
│ [1]   │ 📥 View Inbox    │ List all files in Inbox     │
│ [2]   │ ⏳ View Tasks    │ Scrollable view (U/D nav)   │
│ [3]   │ ▶️ Process Tasks │ Professional AI workflow    │
│ [4]   │ 📋 Create Plan   │ Generate strategic plan     │
│ [5]   │ 📊 Dashboard     │ View full dashboard content │
│ [6]   │ 📝 System Log    │ View activity logs          │
│ [7]   │ 🔄 Refresh       │ Reload all data             │
│ [q]   │ 🚪 Quit          │ Exit application            │
└───────┴──────────────────┴─────────────────────────────┘
```

### Process Tasks Workflow

```
┌────────────────────────────────────────────────────────┐
│  Step 1: Press [3]                                     │
│          ↓                                             │
│  ┌──────────────────────────────────────────────────┐ │
│  │  🤖 AI Agent Required                            │ │
│  │                                                  │ │
│  │  Open any CLI agent (Gemini, Claude, Qwen)      │ │
│  │  and ask it to: "Process Tasks"                  │ │
│  │                                                  │ │
│  │  The AI agent will:                              │ │
│  │    • Read all task files in Needs_Action/        │ │
│  │    • Mark each task as completed                 │ │
│  │    • Move files to Done/                         │ │
│  │    • Update Dashboard.md and System_Log.md       │ │
│  │                                                  │ │
│  │  When done, press any key to continue...         │ │
│  └──────────────────────────────────────────────────┘ │
│          ↓                                             │
│  Step 2: Open another terminal                         │
│          ↓                                             │
│  Step 3: Run AI agent (e.g., "claude")                 │
│          ↓                                             │
│  Step 4: Say "Process Tasks"                           │
│          ↓                                             │
│  Step 5: Wait for completion                           │
│          ↓                                             │
│  Step 6: Return to CLI, press Enter                    │
│          ↓                                             │
│  ┌──────────────────────────────────────────────────┐ │
│  │  ✓ Welcome back! Data refreshed.                 │ │
│  │  Current pending tasks: 0                        │ │
│  │  Press Enter to return to menu...                │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 📋 Demo Tasks

Three demo tasks are pre-created for testing:

| # | Task | Priority | Description |
|---|------|----------|-------------|
| 1 | `task_client_meeting_notes.txt.md` | 🔴 High | Client meeting notes requiring review |
| 2 | `task_invoice_2026_001.pdf.md` | 🟡 Medium | Invoice document for payment processing |
| 3 | `task_team_feedback.md.md` | 🟢 Low | Team feedback for quarterly review |

### Testing the System

```bash
# 1. Run the CLI
py ai_employee.py

# 2. View pending tasks (Option 2)
# You'll see 0 tasks (already processed)

# 3. Check completed tasks (Done/ folder)
# You'll see 5 completed task files

# 4. Drop a new file in Inbox/
echo "Test content" > Inbox/test_file.txt

# 5. Wait 5 seconds (file watcher detects it)

# 6. View pending tasks again (Option 2)
# New task created!

# 7. Process tasks (Option 3)
# Follow the professional workflow
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named ``rich`` | Dependencies not installed | Run ``pip install -r requirements.txt`` |
| File watcher not detecting files | Script not running | Ensure `ai_employee.py` is running |
| Tasks not processing | AI agent not available | Open Claude/Gemini/Qwen CLI separately |
| Dashboard not updating | File permissions | Check write permissions for `.md` files |

### Error Logs

Check `Logs/watcher_errors.log` for file watcher errors.

### Reset System

```bash
# Clear processed files tracker
del Logs\processed_files.txt

# Restart the CLI
py ai_employee.py
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 👨‍💻 Developer

**Imam Sanghaar Chandio**  
*Prompt Engineer, Web Developer*

- 📧 imamsanghaar@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274)
- 🌐 [GitHub](https://github.com/imsanghaar)
- 🔗 [Portfolio](https://imsanghaar.vercel.app)

---

## 🏆 Completion Status

**Bronze Tier of Hackathon 0 is COMPLETED** ✅

**Completion Date:** Tuesday, February 24, 2026

**Delivered:**
- ✅ Obsidian vault structure with all folders
- ✅ Dashboard.md, Company_Handbook.md, System_Log.md
- ✅ Working file_watcher.py with error handling
- ✅ log_manager.py for log rotation
- ✅ Agent Skills in `.claude/skills/`
- ✅ ai_employee.py - Unified interactive CLI
- ✅ Auto-refresh background thread (3s intervals)
- ✅ Live dashboard mode (`--dashboard`)
- ✅ Professional task processing workflow

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Built with ❤️ by ISC for Hackathon 0

[Report Bug](https://github.com/imsanghaar/Hackathon-0/issues) · [Request Feature](https://github.com/imsanghaar/Hackathon-0/issues)

</div>

---

# 🥈 AI Employee System - Silver Tier

> **By Imam Sanghaar Chandio** | Hackathon 0 - Advanced Automation Layer
> Production-Ready Scheduler with Human Approval, Task Planning & Continuous Monitoring

[![Status](https://img.shields.io/badge/status-complete-brightgreen)](https://github.com/imsanghaar/Hackathon-0)
[![Tier](https://img.shields.io/badge/tier-silver-silver)](https://github.com/imsanghaar/Hackathon-0)

---

## 📋 Silver Tier Table of Contents

- [Overview](#-silver-tier-overview)
- [Architecture](#-silver-tier-architecture)
- [Features](#-silver-tier-features)
- [Skills Documentation](#-silver-tier-skills)
- [Quick Start](#-silver-tier-quick-start)
- [Commands Reference](#-commands-reference)
- [Testing](#-testing)

---

## 🎯 Silver Tier Overview

The **Silver Tier** extends the Bronze foundation with production-ready automation features including a configurable scheduler, human approval workflow, intelligent task planning, and continuous monitoring capabilities.

### New Capabilities

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SILVER TIER ADDITIONS                            │
├─────────────────────────────────────────────────────────────────────────┤
│  🔄 SCHEDULER  →  👁️ WATCHER  →  📋 PLANNER  →  ✅ APPROVAL            │
│  Run loops       Monitor Inbox  Create plans  Human sign-off           │
│  (6 min)         folder         step-by-step  required                 │
│                                                                         │
│  🔒 LOCK FILE  →  📝 LOG ROTATION  →  ⏰ TIMEOUT  →  📊 STATUS          │
│  Prevent dupes  Rotate at 4MB     Auto-reject   Check running          │
│                                 (2 hours)       state                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Silver Tier Architecture

### Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI EMPLOYEE SYSTEM                                │
│                         Silver Tier Architecture                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              🔄 SCHEDULER (run_ai_employee.py)                      │   │
│  │         --daemon │ --once │ --status │ --force                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🔒 LOCK FILE  │  📝 LOG ROTATION (4MB)  │  👁️ WATCHER              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📋 PLANNER  │  ✅ APPROVAL  │  AI EMPLOYEE (Bronze)                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │ Inbox/       │     │ Needs_Action/│     │ Done/        │                │
│  │ (New .md)    │     │ (Plans)      │     │ (Completed)  │                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Silver Tier Features

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Scheduler** | Run watcher + planner in configurable loops | ✅ |
| **Daemon Mode** | Continuous execution (default 6 min) | ✅ |
| **Once Mode** | Single execution for testing | ✅ |
| **Status Mode** | View scheduler state | ✅ |
| **Lock File** | Prevent duplicate instances | ✅ |
| **Log Rotation** | Auto-archive logs at 4MB | ✅ |
| **Cross-Platform** | Windows + Linux + Mac | ✅ |

### Vault Watcher Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Continuous Monitoring** | Watch AI_Employee_Vault/Inbox | ✅ |
| **Randomized Interval** | 10-30 seconds | ✅ |
| **Duplicate Prevention** | Track processed files | ✅ |
| **AI Processing Trigger** | Auto-trigger workflow | ✅ |

### Task Planner Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Content Analysis** | Parse frontmatter and body | ✅ |
| **Step Generation** | Create execution plans | ✅ |
| **Auto Move** | Move to Done/ when processed | ✅ |
| **Idempotent** | Process each file once | ✅ |

### Human Approval Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Approval Monitoring** | Check for pending approvals | ✅ |
| **Status Detection** | Detect Approved/Rejected | ✅ |
| **File Renaming** | .approved, .rejected, .timeout | ✅ |
| **Configurable Timeout** | Default 2 hours | ✅ |

---

## 🤖 Silver Tier Skills

### Skill Documentation

| Skill | Location | Description |
|-------|----------|-------------|
| **vault-watcher** | [`.claude/skills/vault-watcher/`](.claude/skills/vault-watcher/) | Monitor Inbox, trigger AI processing |
| **task-planner** | [`.claude/skills/task-planner/`](.claude/skills/task-planner/) | Analyze files, create plans |
| **human-approval** | [`.claude/skills/human-approval/`](.claude/skills/human-approval/) | Human sign-off workflow |
| **schedular-silvertier** | [`.claude/skills/schedular-silvertier/`](.claude/skills/schedular-silvertier/) | Run watcher + planner loops |

### Quick Links to Skill Docs

- 📄 [Vault Watcher Skill](.claude/skills/vault-watcher/SKILL.md)
- 📄 [Task Planner Skill](.claude/skills/task-planner/SKILL.md)
- 📄 [Human Approval Skill](.claude/skills/human-approval/SKILL.md)
- 📄 [Scheduler Skill](.claude/skills/schedular-silvertier/SKILL.md)

---

## 🚀 Silver Tier Quick Start

### Prerequisites

- Python 3.x (Windows/Linux/Mac)
- Bronze Tier installed and working

### Installation

```bash
cd E:\ai_employee\[Bronze_Tier](Silver_Tier)

# Verify scripts
dir scripts\
# Should show: run_ai_employee.py, watch_inbox.py, task_planner.py, requests-approval.py
```

### First Run

```bash
# Check status
python scripts/run_ai_employee.py --status

# Run single cycle
python scripts/run_ai_employee.py --once

# Start daemon mode
python scripts/run_ai_employee.py --daemon
```

---

## 💻 Commands Reference

### Scheduler Commands

```bash
# Check status (no lock required)
python scripts/run_ai_employee.py --status

# Run single cycle
python scripts/run_ai_employee.py --once

# Daemon mode (continuous, 6 min interval)
python scripts/run_ai_employee.py --daemon

# Custom interval (5 minutes)
python scripts/run_ai_employee.py --daemon --interval 300

# Force start (ignore lock)
python scripts/run_ai_employee.py --daemon --force
```

### Vault Watcher Commands

```bash
# Run watcher directly
python scripts/watch_inbox.py
```

### Task Planner Commands

```bash
# Process all files
python scripts/task_planner.py

# Process specific file
python scripts/task_planner.py --file example.md

# Dry run (preview)
python scripts/task_planner.py --dry-run
```

### Human Approval Commands

```bash
# Check approvals
python scripts/requests-approval.py

# Custom timeout (1 hour)
python scripts/requests-approval.py --timeout 3600

# Watch mode (continuous)
python scripts/requests-approval.py --watch --interval 60

# Dry run
python scripts/requests-approval.py --dry-run
```

### Quick Reference Table

| Command | Description |
|---------|-------------|
| `python scripts/run_ai_employee.py --status` | Check scheduler status |
| `python scripts/run_ai_employee.py --once` | Single execution |
| `python scripts/run_ai_employee.py --daemon` | Continuous monitoring |
| `python scripts/watch_inbox.py` | Run vault watcher |
| `python scripts/task_planner.py` | Run task planner |
| `python scripts/requests-approval.py` | Check approvals |

---

## 🧪 Testing

### Run Test Suite

```bash
python scripts/test_implementations.py
```

### Test Results

| Component | Tests | Passed | Failed |
|-----------|-------|--------|--------|
| Vault Watcher | 6 | 6 | 0 |
| Task Planner | 8 | 8 | 0 |
| Integration | 3 | 3 | 0 |
| Human Approval | 7 | 7 | 0 |
| Scheduler | 8 | 8 | 0 |
| **TOTAL** | **35** | **35** | **0** |

**Pass Rate:** 100% ✅

### Test Documentation

Full test results: [`scripts/tests.md`](scripts/tests.md)

---

## 📁 Silver Tier Folder Structure

```
Hackathon-0/
│
├── .claude/skills/
│   ├── vault-watcher/           # [Silver] Monitor Inbox
│   ├── task-planner/            # [Silver] Analyze & plan
│   ├── human-approval/          # [Silver] Human sign-off
│   └── schedular-silvertier/    # [Silver] Scheduler
│
├── AI_Employee_Vault/           # [Silver] Vault structure
│   ├── Inbox/                   # Drop .md files here
│   ├── Needs_Action/            # Plans pending approval
│   └── Done/                    # Completed items
│
├── scripts/                     # [Silver] All scripts
│   ├── run_ai_employee.py       # Main scheduler
│   ├── watch_inbox.py           # Vault watcher
│   ├── task_planner.py          # Task planner
│   ├── requests-approval.py     # Approval checker
│   └── test_implementations.py  # Test suite
│
├── Logs/
│   ├── ai_employee.log          # [Silver] Scheduler log
│   ├── action.log               # [Silver] All actions
│   └── scheduler.lock           # [Silver] Lock file
│
└── [Bronze Tier Files...]
    ├── ai_employee.py
    ├── file_watcher.py
    └── ...
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fcntl'` | Fixed - cross-platform support added |
| Scheduler won't start | Remove lock: `del Logs\scheduler.lock` or use `--force` |
| Approval not detected | Use `**Status:** Approved` exactly |
| Log file too large | Auto-rotates at 4MB threshold |

---

## 🏆 Silver Tier Completion

**Status:** ✅ COMPLETE

**Completion Date:** Tuesday, February 24, 2026

**Delivered:**
- ✅ Scheduler with daemon/once/status modes
- ✅ Vault watcher with randomized intervals
- ✅ Task planner with content analysis
- ✅ Human approval workflow with timeout
- ✅ Lock file for duplicate prevention
- ✅ Log rotation at 4MB threshold
- ✅ Cross-platform support (Windows/Linux/Mac)
- ✅ Comprehensive testing (35/35 tests pass)

---

## 👨‍💻 Developer

**Imam Sanghaar Chandio**
*Prompt Engineer, Web Developer*

- 📧 imamsanghaar@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274)
- 🌐 [GitHub](https://github.com/imsanghaar)
- 🔗 [Portfolio](https://imsanghaar.vercel.app)

---

**Last Updated:** February 24, 2026
**Version:** 2.0 (Silver Tier)

---

# 🚀 How to Run Silver Tier AI Employee

## Quick Start Guide

### Step 1: Verify Installation

```bash
cd E:\ai_employee\[Bronze_Tier](Silver_Tier)

# Check Python version (need 3.x)
python --version

# Verify required files exist
dir scripts\
# Should show: run_ai_employee.py, watch_inbox.py, task_planner.py, requests-approval.py

# Verify skills exist
dir .claude\skills\
# Should show 9 skill folders
```

### Step 2: Configure Environment

```bash
# Check .env file exists
dir .env

# Required environment variables:
# - EMAIL_ADDRESS (for Gmail sending)
# - EMAIL_PASSWORD (Gmail app password)
# - LINKEDIN_EMAIL (for LinkedIn posting)
# - LINKEDIN_PASSWORD (LinkedIn password)
```

### Step 3: Start Silver Tier

**Option A: Interactive CLI (Recommended for beginners)**
```bash
python ai_employee.py
```

**Option B: Scheduler Daemon Mode (Production)**
```bash
# Start continuous monitoring (runs every 6 minutes)
python scripts\run_ai_employee.py --daemon

# Or with custom interval (5 minutes)
python scripts\run_ai_employee.py --daemon --interval 300
```

**Option C: Single Execution (Testing)**
```bash
# Run one cycle only
python scripts\run_ai_employee.py --once
```

### Step 4: Monitor Status

```bash
# Check scheduler status
python scripts\run_ai_employee.py --status

# View logs
type Logs\ai_employee.log

# Check pending tasks
python .claude\skills\vault-file-manager\scripts\move_task.py --list
```

---

## 📁 Silver Tier Files Reference

### Core Scripts (scripts/)

| File | Purpose | How to Run |
|------|---------|------------|
| `run_ai_employee.py` | **Main scheduler** - runs watcher + planner loops | `python scripts\run_ai_employee.py --daemon` |
| `watch_inbox.py` | **Vault watcher** - monitors Inbox for new .md files | `python scripts\watch_inbox.py` |
| `task_planner.py` | **Task planner** - analyzes files, creates plans | `python scripts\task_planner.py` |
| `requests-approval.py` | **Approval checker** - processes human approvals | `python scripts\requests-approval.py` |
| `test_implementations.py` | **Test suite** - verifies all components | `python scripts\test_implementations.py` |

### Agent Skills (.claude/skills/)

| Skill Folder | Purpose | Trigger Phrase |
|--------------|---------|----------------|
| `gmail-send/` | Send emails via SMTP | Use script directly |
| `linkedin-post/` | Post to LinkedIn automatically | Use script directly |
| `vault-file-manager/` | Move files between vault folders | Use script directly |
| `human-approval/` | Human-in-the-loop approval workflow | "Check approvals" |
| `task-planner/` | Create execution plans from inbox files | "Plan inbox files" |
| `make-plan-for-tasks/` | Strategic planning for pending tasks | "Make a Plan for tasks" |
| `schedular-silvertier/` | Run scheduler loops | "Start scheduler" |
| `vault-watcher/` | Monitor vault inbox | "Run vault watcher" |
| `process-tasks/` | Complete pending tasks | "Process Tasks" |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (EMAIL, LINKEDIN credentials) |
| `.env.example` | Template for .env file |
| `requirements.txt` | Python dependencies |

### Log Files (Logs/)

| File | Purpose |
|------|---------|
| `ai_employee.log` | Scheduler execution logs |
| `action.log` | All AI actions log |
| `file_movements.log` | File movement history |
| `emails_sent.log` | Sent emails log |
| `scheduler.lock` | Prevents duplicate scheduler instances |

### Vault Folders (AI_Employee_Vault/)

| Folder | Purpose |
|--------|---------|
| `Inbox/` | Drop new .md files here for processing |
| `Needs_Action/` | Contains pending plans and tasks |
| `Done/` | Completed tasks and processed files |
| `Needs_Approval/` | Files waiting for human approval |

---

## 🎯 Common Workflows

### Workflow 1: Process New File

```bash
# 1. Create new file in Inbox
echo "Task content" > AI_Employee_Vault\Inbox\new_task.md

# 2. Wait 10-30 seconds (vault-watcher detects it)

# 3. Task planner creates plan in Needs_Action/

# 4. Review and approve if needed

# 5. Process with AI agent
```

### Workflow 2: Send Email

```bash
python .claude\skills\gmail-send\scripts\send_email.py ^
  --to "recipient@example.com" ^
  --subject "Meeting Tomorrow" ^
  --body "Hi, just reminding you about our meeting tomorrow at 2 PM."
```

### Workflow 3: Post to LinkedIn

```bash
python .claude\skills\linkedin-post\scripts\linkedin_auto.py ^
  --text "Excited to announce our new product launch! #innovation"
```

### Workflow 4: Human Approval

```bash
# 1. Create approval request in Needs_Approval/
# 2. Review and add status marker:
#    Status: Approved
#    Approved by: Your Name
# 3. Run approval checker
python scripts\requests-approval.py
```

---

## ⚙️ Production Deployment

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily or At startup
4. Action: Start a program
5. Program: `python`
6. Arguments: `E:\ai_employee\[Bronze_Tier](Silver_Tier)\scripts\run_ai_employee.py --daemon`
7. Start in: `E:\ai_employee\[Bronze_Tier](Silver_Tier)`

### Linux Cron

```bash
# Edit crontab
crontab -e

# Add line to run every 6 minutes
*/6 * * * * cd /path/to/project && python scripts/run_ai_employee.py --once
```

---

## 📊 Monitoring & Maintenance

### Check System Health

```bash
# Scheduler status
python scripts\run_ai_employee.py --status

# View recent logs
tail -50 Logs\ai_employee.log

# Check pending tasks
dir AI_Employee_Vault\Needs_Action\

# Check completed tasks
dir AI_Employee_Vault\Done\
```

### Clear Old Logs

```bash
# Archive logs older than 7 days
# (Manual or script-based cleanup)
```

### Reset System

```bash
# Remove lock file if scheduler stuck
del Logs\scheduler.lock

# Clear processed files tracker
type nul > Logs\processed_files.txt

# Restart scheduler
python scripts\run_ai_employee.py --daemon
```

---

## 🆘 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Scheduler won't start | Delete `Logs\scheduler.lock` or use `--force` |
| Email not sending | Check EMAIL_PASSWORD (use app password, not regular password) |
| LinkedIn post fails | Ensure browser is not in incognito mode, clear cache |
| Approval not detected | Use exact format: `Status: Approved` |
| File not moving | Check folder permissions, ensure folders exist |
| High memory usage | Check log rotation is working (4MB limit) |

---

## 📞 Support

- **Documentation:** See `SILVER_TIER_ANALYSIS.md` for requirements analysis
- **Test Results:** See `scripts\tests.md` for test documentation
- **Issues:** Report on GitHub
- **Developer:** imamsanghaar@gmail.com

---

<div align="center">

**🥈 Silver Tier Complete!**

Built with ❤️ by **Imam Sanghaar Chandio** for Hackathon 0

[Report Bug](https://github.com/imsanghaar/Hackathon-0/issues) · [Request Feature](https://github.com/imsanghaar/Hackathon-0/issues)

</div>
