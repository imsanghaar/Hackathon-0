# 🤖 AI Employee System (Digital FTE)

> **A Full-Time Equivalent (FTE) Digital Employee Powered by AI**  
> An intelligent automation system that monitors folders, creates tasks, processes them with AI agents, and manages workflows automatically—working 24/7 like a real employee.

**By Imam Sanghaar Chandio & Qwen Code**

[![Status](https://img.shields.io/badge/status-complete-brightgreen)](https://github.com/imsanghaar/Hackathon-0)
[![Python](https://img.shields.io/badge/python-3.x-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

### 🏷️ Tags

`status:complete` `tier:bronze` `tier:silver` `automation` `ai-employee` `digital-fte` `workflow` `task-management`

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/imsanghaar/Hackathon-0.git
cd Hackathon-0
pip install -r requirements.txt

# Run the interactive CLI
python ai_employee.py
```

---

## 📖 Table of Contents

1. [Bronze Tier](#-bronze-tier) - Core CLI & File Monitoring
2. [Silver Tier](#-silver-tier) - Scheduler, Approval & Planning
3. [Developers](#-developers)
4. [Contributors](#-contributors)

---

# 🥉 Bronze Tier

> **Foundation Layer** - Interactive CLI with real-time file monitoring and task management

## Overview

The Bronze Tier provides the core functionality of the AI Employee System:

```
📥 Inbox → 📝 Auto-Create Tasks → 🤖 AI Processing → ✅ Done
```

## Features

| Feature | Description |
|---------|-------------|
| **File Monitoring** | Watches Inbox/ every 5 seconds for new files |
| **Auto Task Creation** | Creates structured task files with YAML frontmatter |
| **Interactive CLI** | Beautiful menu-driven interface with live stats |
| **AI Agent Integration** | Works with Claude, Gemini, Qwen via agent skills |
| **Dashboard & Logs** | Auto-updated Dashboard.md and System_Log.md |
| **Duplicate Prevention** | Tracks processed files to avoid duplicates |

## Folder Structure

```
Hackathon-0/
├── .claude/skills/          # AI Agent Skills
├── Inbox/                   # 📥 Drop new files here
├── Needs_Action/            # ⏳ Pending tasks (auto-created)
├── Done/                    # ✅ Completed tasks (auto-moved)
├── Logs/                    # 📝 System logs
├── Plans/                   # 📋 Strategic plans
│
├── ai_employee.py           # 🎮 Main interactive CLI
├── file_watcher.py          # 👁️ File system monitor
├── log_manager.py           # 🔄 Log rotation
│
├── Dashboard.md             # 📊 Task overview
├── System_Log.md            # 📝 Activity log
├── Company_Handbook.md      # 📜 Guidelines
└── README.md                # 📖 This file
```

## Usage

```bash
# Interactive CLI (default)
python ai_employee.py

# Live dashboard mode
python ai_employee.py --dashboard

# File watcher only
python ai_employee.py --watch
```

### Menu Options

| Key | Action | Description |
|-----|--------|-------------|
| `1` | 📥 View Inbox | List files in Inbox |
| `2` | ⏳ View Tasks | View pending tasks |
| `3` | ▶️ Process Tasks | Process with AI agent |
| `4` | 📋 Create Plan | Generate strategic plan |
| `5` | 📊 Dashboard | View full dashboard |
| `6` | 📝 System Log | View activity logs |
| `7` | 🔄 Refresh | Reload all data |
| `q` | 🚪 Quit | Exit application |

## Documentation

| Document | Description |
|----------|-------------|
| [Company_Handbook.md](Company_Handbook.md) | System guidelines |
| [Dashboard.md](Dashboard.md) | Current task overview |
| [System_Log.md](System_Log.md) | Activity history |

---

# 🥈 Silver Tier

> **Advanced Automation Layer** - Production-ready scheduler with human approval and continuous monitoring

## Enhancements Over Bronze

| Feature | Bronze | Silver |
|---------|--------|--------|
| File Monitoring | ✅ Manual CLI | ✅ Daemon Scheduler |
| Task Planning | ✅ Basic | ✅ Strategic Plans |
| Human Approval | ❌ | ✅ Approval Workflow |
| Continuous Run | ❌ | ✅ 6-min Intervals |
| Lock File | ❌ | ✅ Prevents Duplicates |
| Log Rotation | ✅ Basic | ✅ 4MB Auto-Archive |

## New Features

| Feature | Description |
|---------|-------------|
| **Scheduler Daemon** | Runs watcher + planner in configurable loops (default 6 min) |
| **Human Approval** | Tasks require "Status: Approved" before execution |
| **Task Planner** | Analyzes files and creates step-by-step execution plans |
| **Lock File System** | Prevents duplicate scheduler instances |
| **Log Rotation** | Auto-archives logs at 4MB to prevent bloat |
| **Cross-Platform** | Windows, Linux, Mac support |

## Silver Tier Commands

```bash
# Check scheduler status
python scripts/run_ai_employee.py --status

# Run single cycle
python scripts/run_ai_employee.py --once

# Daemon mode (continuous)
python scripts/run_ai_employee.py --daemon

# Custom interval (5 minutes)
python scripts/run_ai_employee.py --daemon --interval 300

# Force start (ignore lock)
python scripts/run_ai_employee.py --daemon --force
```

## Silver Tier Scripts

| Script | Description |
|--------|-------------|
| `scripts/run_ai_employee.py` | Main scheduler daemon |
| `scripts/watch_inbox.py` | Vault Inbox watcher |
| `scripts/task_planner.py` | Task analyzer & planner |
| `scripts/requests-approval.py` | Approval status checker |
| `scripts/test_implementations.py` | Test suite |

## Silver Tier Documentation

| Document | Description |
|----------|-------------|
| [SILVER_TIER_VERIFICATION.md](SILVER_TIER_VERIFICATION.md) | Requirements checklist |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | MCP server setup |
| [scripts/tests.md](scripts/tests.md) | Test results |

---

## 🤖 Agent Skills

Agent Skills are documented behaviors for AI agents to interact with the vault system.

| Skill | Trigger | Action |
|-------|---------|--------|
| **Process Tasks** | `"Process Tasks"` | Complete tasks, update Dashboard & Log |
| **Make a Plan** | `"Make a Plan for tasks"` | Create strategic planning document |

Skills located in `.claude/skills/` with detailed `SKILL.md` documentation.

---

## 👨‍💻 Developers

### Lead Developer

**Imam Sanghaar Chandio**  
*Prompt Engineer, Web Developer*

- 📧 imamsanghaar@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274)
- 🌐 [GitHub](https://github.com/imsanghaar)
- 💼 [Portfolio](https://imsanghaar.vercel.app)

---

## 🤝 Contributors

| Name | Role | Links |
|------|------|-------|
| **Imam Sanghaar Chandio** | Creator & Lead Developer | [GitHub](https://github.com/imsanghaar) • [LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274) |
| **Qwen Code** | AI Development Assistant | [Alibaba Cloud](https://www.alibabacloud.com/) |
| **Claude Code** | AI Development Assistant | [Anthropic](https://www.anthropic.com/) |

---

## 🏆 Status

**Bronze Tier:** ✅ Complete  
**Silver Tier:** ✅ Complete

**Last Updated:** February 28, 2026

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Built with ❤️ by Imam Sanghaar Chandio, Qwen Code & Claude Code

[Report Bug](https://github.com/imsanghaar/Hackathon-0/issues) · [Request Feature](https://github.com/imsanghaar/Hackathon-0/issues)

</div>
