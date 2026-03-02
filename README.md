# 🤖 AI Employee System (Digital FTE)

> **A Full-Time Equivalent (FTE) Digital Employee Powered by AI**  
> An autonomous automation system that monitors communication channels, creates execution plans, and processes tasks using specialized AI Agent Skills—working 24/7 with human-in-the-loop oversight.

<div align="center">

[![Status: Complete](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Bronze](https://img.shields.io/badge/Tier-Bronze-CD7F32?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Silver](https://img.shields.io/badge/Tier-Silver-lightgrey?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Gold](https://img.shields.io/badge/Tier-Gold-gold?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)](https://python.org)
[![MCP: Enabled](https://img.shields.io/badge/MCP-Enabled-orange?style=for-the-badge)](https://modelcontextprotocol.io)

**🏆 GOLD TIER IMPLEMENTED**

[Quick Start](#-quick-start) • [Documentation](#-documentation) • [Team](#-development-team)

</div>

---

## 📋 Overview

The AI Employee System is a **multi-tier automation framework** designed to handle business workflows autonomously. From simple file monitoring to complex browser-based tasks like LinkedIn posting and Gmail management, the system operates through a modular **"Agent Skill"** architecture.

### Key Capabilities

- **📊 Multi-Channel Monitoring** — Watches local folders, Gmail, and social media for new tasks
- **🔄 Strategic Planning** — Automatically generates detailed `Plan.md` files for complex requests
- **🤖 Autonomous Execution** — Ralph Wiggum loop for multi-step task completion
- **🛡️ Error Recovery** — Automatic retry and graceful degradation on failures
- **📧 Email & Social** — LinkedIn automation, Gmail integration, and social media logging
- **👤 Human-in-the-Loop** — Sensitive actions require explicit human approval via the vault
- **📈 CEO Briefing** — Weekly business audit with comprehensive reports

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for MCP server)
- Chrome/Edge browser (for Playwright)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/imsanghaar/Hackathon-0.git
cd Hackathon-0

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Gmail and LinkedIn credentials
```

### Start the System

```bash
# Start MCP Server (required for browser automation)
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Start the main scheduler (Gold Tier - Full Autonomous Mode)
python scripts/run_ai_employee.py --daemon
```

This runs the complete cycle every 6 minutes:
1. **Error Recovery** — Process retry queue
2. **Vault Watcher** — Check for new files
3. **Gmail Watcher** — Monitor emails
4. **Task Planner** — Create execution plans
5. **Ralph Wiggum** — Autonomous task execution
6. **CEO Briefing** — Weekly reports (on schedule)

---

## 🥇 Gold Tier: Autonomous Employee

### Features Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| Error Recovery System | ✅ | Automatic retry, graceful degradation |
| Ralph Wiggum Autonomous Loop | ✅ | Iterative multi-step task execution |
| Weekly CEO Briefing | ✅ | Business + Accounting audit reports |
| Social Media Summary | ✅ | LinkedIn activity logging |
| Comprehensive Audit Logging | ✅ | Multi-domain logging with rotation |
| 16 Agent Skills | ✅ | All AI functionality modularized |

### Folder Structure

```
Hackathon-0/
├── .claude/skills/           # All 16 Agent Skills
│   ├── ceo-briefing/         # Weekly CEO reports
│   ├── error-recovery/       # Error handling & retry
│   ├── ralph-wiggum/         # Autonomous loop
│   ├── social-summary/       # Social media logging
│   ├── gmail-watcher/        # Gmail monitoring
│   ├── gmail-send/           # Email sending
│   ├── linkedin-auto-post/   # LinkedIn automation
│   ├── linkedin-post/        # LinkedIn posting
│   ├── human-approval/       # Approval workflow
│   ├── task-planner/         # Plan.md generation
│   ├── make-plan-for-tasks/  # Task planning
│   ├── process-tasks/        # Task execution
│   ├── vault-watcher/        # Vault monitoring
│   ├── vault-file-manager/   # File operations
│   ├── accounting-manager/   # Accounting tracking
│   └── schedular-silvertier/ # Scheduler daemon
├── AI_Employee_Vault/        # Gold Tier Vault
│   ├── Inbox/                # New tasks
│   ├── Needs_Action/         # Pending tasks
│   ├── Needs_Approval/       # Awaiting approval
│   ├── Done/                 # Completed tasks
│   ├── Errors/               # Failed tasks (error recovery)
│   ├── Reports/              # CEO Weekly Briefing
│   ├── Reposts/              # Social media logs
│   └── Accounting/           # Financial records
├── Plans/                    # Generated execution plans
├── Logs/                     # Comprehensive audit logs
└── mcp/                      # MCP Servers
    └── business-mcp/         # Business actions server
```

### Gold Tier Commands

| Command | Description |
|---------|-------------|
| `python scripts/run_ai_employee.py --daemon` | Start full autonomous loop |
| `python scripts/run_ai_employee.py --once` | Run single cycle |
| `python scripts/run_ai_employee.py --status` | Check scheduler status |
| `python ralph_wiggum.py --run` | Run autonomous task loop |
| `python error_recovery.py --check` | Process error retry queue |
| `python generate_ceo_briefing.py` | Generate weekly report |
| `python social_summary.py --log -c "Content"` | Log social media post |
| `python task_planner.py` | Create execution plans |
| `python watch_gmail.py --watch` | Monitor Gmail continuously |
| `python auto_post.py` | Execute LinkedIn posts |

### Monitoring & Audit

```bash
# View Dashboard
cat Dashboard.md

# View System Log
cat System_Log.md

# View CEO Weekly Briefing
cat AI_Employee_Vault/Reports/CEO_Weekly.md

# View Error Log
cat Logs/errors.log

# View Social Media Log
cat AI_Employee_Vault/Reposts/Social_Log.md

# Check Active Loops
python .claude/skills/ralph-wiggum/scripts/ralph_wiggum.py --status
```

---

## 🥈 Silver Tier: Advanced Automation

### Features

- ✅ All Bronze Requirements
- ✅ Multiple Watchers (Gmail + File + Vault)
- ✅ LinkedIn Auto-Post for Business
- ✅ Plan.md Generation (Strategic Reasoning)
- ✅ MCP Server (External Actions)
- ✅ Human-in-the-Loop Approval
- ✅ Scheduling (Daemon with Lock Files)

### Running Silver Tier

```bash
# Start MCP Server
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Gmail Watcher
python .claude/skills/gmail-watcher/scripts/watch_gmail.py --watch --interval 300

# LinkedIn Auto-Post
python .claude/skills/linkedin-auto-post/scripts/auto_post.py

# Approval Checker
python .claude/skills/human-approval/scripts/request_approval.py --check

# Task Planner
python scripts/task_planner.py
```

---

## 🥉 Bronze Tier: Core Foundation

### Features

- ✅ Obsidian Vault (Dashboard.md + Company_Handbook.md)
- ✅ File Watcher Script
- ✅ Basic Folders (/Inbox, /Needs_Action, /Done)
- ✅ 16 Agent Skills Modularized

### Running Bronze Tier

```bash
# Interactive CLI
python ai_employee.py

# File Watcher
python scripts/watch_inbox.py

# Live Dashboard
python ai_employee.py --dashboard
```

---

## 🛠️ Architecture: Agent Skills

All AI functionality is decoupled into **16 Skills** located in `.claude/skills/`. Each skill includes a `SKILL.md` defining its behavior and Python scripts for execution.

| Skill | Purpose | Tier |
|-------|---------|------|
| `gmail-watcher` | Monitors Gmail for task-related emails | Silver |
| `gmail-send` | Sends emails via SMTP | Silver |
| `linkedin-post` | Automates LinkedIn content publishing | Silver |
| `linkedin-auto-post` | Scans and posts LinkedIn requests | Silver |
| `task-planner` | Creates step-by-step execution plans | Silver |
| `make-plan-for-tasks` | Plan.md file generator | Silver |
| `process-tasks` | Task execution engine | Bronze |
| `human-approval` | Manages approval/rejection workflow | Silver |
| `vault-watcher` | Monitors vault folders | Bronze |
| `vault-file-manager` | Handles file movements | Bronze |
| `error-recovery` | Error handling and retry system | Gold |
| `ralph-wiggum` | Autonomous multi-step loop | Gold |
| `ceo-briefing` | Weekly business audit reports | Gold |
| `social-summary` | Social media activity logging | Gold |
| `accounting-manager` | Financial tracking | Gold |
| `schedular-silvertier` | Production scheduler daemon | Silver |

---

## 📊 Documentation

| Document | Description |
|----------|-------------|
| **[Dashboard.md](Dashboard.md)** | Real-time task statistics and system health |
| **[Company_Handbook.md](Company_Handbook.md)** | Operational guidelines and tier definitions |
| **[MCP_INTEGRATION.md](MCP_INTEGRATION.md)** | Model Context Protocol setup guide |
| **[System_Log.md](System_Log.md)** | Chronological log of autonomous actions |
| **[CEO_Weekly.md](AI_Employee_Vault/Reports/CEO_Weekly.md)** | Weekly business audit report |
| **[Social_Log.md](AI_Employee_Vault/Reposts/Social_Log.md)** | Social media activity archive |

---

## 📁 Key File Locations

| Component | Location |
|-----------|----------|
| All Agent Skills | `.claude/skills/` |
| Main Scheduler | `scripts/run_ai_employee.py` |
| Interactive CLI | `ai_employee.py` |
| Task Planner | `scripts/task_planner.py` |
| MCP Server | `mcp/business-mcp/server.py` |
| Error Logs | `Logs/` |
| Generated Plans | `Plans/` |
| Vault Data | `AI_Employee_Vault/` |
| CEO Reports | `AI_Employee_Vault/Reports/` |
| Social Logs | `AI_Employee_Vault/Reposts/` |

---

## 👨‍💻 Development Team

**Imam Sanghaar Chandio**  
*Lead Developer & Prompt Engineer*

[📧 Email](mailto:imamsanghaar@gmail.com) · [🔗 LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274) · [🌐 GitHub](https://github.com/imsanghaar)

**AI Contributors**
- **Qwen Code** — Architecture & Logic Optimization
- **Claude Code** — Agent Skills & MCP Integration
- **Gemini CLI** — Final Verification, README Refinement & Deployment

---

<div align="center">

## 🌟 Support the Project

**⭐ Star this repo if you find it useful!**

```bash
git clone https://github.com/imsanghaar/Hackathon-0.git
cd Hackathon-0
python scripts/run_ai_employee.py --daemon
```

Built with ❤️ for the AI Automation Hackathon 2026

**🏆 GOLD TIER COMPLETE**

[![Tier: Bronze](https://img.shields.io/badge/Tier-Bronze-CD7F32?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Silver](https://img.shields.io/badge/Tier-Silver-lightgrey?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Gold](https://img.shields.io/badge/Tier-Gold-gold?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)

</div>
