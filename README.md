# 🤖 AI Employee System - Bronze Tier

> **By ISC** | Hackathon 0 - Foundation Layer  
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
| `ModuleNotFoundError: No module named 'rich'` | Dependencies not installed | Run `pip install -r requirements.txt` |
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

---

## 🏆 Completion Status

**Bronze Tier of Hackathon Zero is COMPLETED** ✅

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
