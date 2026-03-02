# 🤖 AI Employee (Digital FTE) - The Autonomous Business Agent

> **An advanced, multi-tier autonomous framework designed to function as a Full-Time Equivalent (FTE) Digital Employee. It monitors communication channels, executes strategic plans, and handles business workflows 24/7 with human-in-the-loop oversight.**

<div align="center">

[![Status: Complete](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Bronze](https://img.shields.io/badge/Tier-Bronze-CD7F32?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Silver](https://img.shields.io/badge/Tier-Silver-lightgrey?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Gold](https://img.shields.io/badge/Tier-Gold-gold?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)](https://python.org)
[![MCP: Enabled](https://img.shields.io/badge/MCP-Enabled-orange?style=for-the-badge)](https://modelcontextprotocol.io)

**🏆 GOLD TIER FULLY IMPLEMENTED**

[Quick Start](#-quick-start) • [Tiers & Features](#-tiered-architecture) • [Architecture](#-agent-skills-architecture) • [Contributors](#-development--contributions)

</div>

---

## 🌟 Overview

The **AI Employee** is a sophisticated automation system that bridges the gap between simple scripts and full autonomous agents. Built on a modular **"Agent Skill"** architecture, it handles everything from mundane file movements to complex strategic reasoning and multi-platform interactions (Gmail, LinkedIn, etc.).

---

## 🏗️ Tiered Architecture

The system is organized into three progressive tiers, each adding a layer of intelligence and autonomy.

### 🥉 Bronze Tier: Core Foundation
*The bedrock of the AI Employee, providing the essential infrastructure for task management.*

- **Features**:
  - **Modular Vault**: Organized folder structure (`Inbox`, `Needs_Action`, `Done`).
  - **Task Monitoring**: Basic file system watching for incoming requests.
  - **Interactive CLI**: Command-line interface for manual task control.
  - **Foundation Skills**: Core skills for file management and basic task execution.
- **📁 Core Location**: [`AI_Employee_Vault/`](AI_Employee_Vault/)

### 🥈 Silver Tier: Advanced Automation
*Enhanced connectivity and strategic reasoning for business operations.*

- **Features**:
  - **Multi-Channel Watchers**: Monitoring Gmail and LinkedIn for incoming business opportunities.
  - **Strategic Planning**: Generation of detailed `Plan.md` files for complex task execution.
  - **LinkedIn Automation**: Automated posting to generate leads and engagement.
  - **MCP Integration**: Model Context Protocol servers for external tool interactions.
  - **Human-in-the-Loop**: Safe approval workflows for sensitive business actions.
- **📁 Core Locations**: [`scripts/`](scripts/), [`mcp/`](mcp/)

### 🥇 Gold Tier: Fully Autonomous Employee
*The pinnacle of autonomy, featuring self-healing loops and executive reporting.*

- **Features**:
  - **Ralph Wiggum Loop**: Continuous autonomous execution of multi-step task chains.
  - **Error Recovery System**: Automatic retry logic and graceful failure handling.
  - **CEO Weekly Briefing**: Automated generation of comprehensive business audit reports.
  - **Accounting Management**: Tracking of financial records and social media logging.
  - **Daemon Mode**: 24/7 background operation with robust logging and status tracking.
- **📁 Core Locations**: [`.claude/skills/`](.claude/skills/), [`AI_Employee_Vault/Reports/`](AI_Employee_Vault/Reports/)

---

## 📊 Feature Comparison

| Feature | Bronze | Silver | Gold |
| :--- | :---: | :---: | :---: |
| File Watching | ✅ | ✅ | ✅ |
| Interactive CLI | ✅ | ✅ | ✅ |
| Vault Organization | ✅ | ✅ | ✅ |
| LinkedIn Posting | ❌ | ✅ | ✅ |
| Strategic Planning (`Plan.md`) | ❌ | ✅ | ✅ |
| Gmail Integration | ❌ | ✅ | ✅ |
| Human Approval Workflow | ❌ | ✅ | ✅ |
| **Autonomous Loop (Ralph Wiggum)** | ❌ | ❌ | ✅ |
| **Automated Error Recovery** | ❌ | ❌ | ✅ |
| **Weekly CEO Audit Reports** | ❌ | ❌ | ✅ |

---

## 🛠️ Agent Skills Architecture

All AI functionality is decoupled into **16 specialized Agent Skills** located in `.claude/skills/`. This allows for easy extension and high reliability.

- **Communication**: `gmail-watcher`, `gmail-send`, `linkedin-post`, `linkedin-auto-post`
- **Reasoning**: `task-planner`, `make-plan-for-tasks`, `ralph-wiggum`
- **Operations**: `vault-file-manager`, `human-approval`, `error-recovery`
- **Analytics**: `ceo-briefing`, `social-summary`, `accounting-manager`

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Node.js 16+ (for MCP)
- Playwright (for LinkedIn automation)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/imsanghaar/Hackathon-0.git
cd Hackathon-0

# Install dependencies
pip install -r requirements.txt
cp .env.example .env  # Configure your credentials
```

### 3. Run the System
```bash
# Start the Gold Tier Autonomous Daemon
python scripts/run_ai_employee.py --daemon
```

---

## 🤝 Development & Contributions

This project is a collaborative effort between human ingenuity and advanced AI.

- **Nemat** — *Lead Architect & Visionary Developer*
- **Gemini CLI** — *Autonomous Engineering, Deployment & Verification*
- **Qwen Code** — *Logic Optimization & Core Architecture*
- **Claude Code** — *Agent Skills & Protocol Integration*

---

<div align="center">

**Built with ❤️ for the AI Automation Hackathon 2026**

[![Star on GitHub](https://img.shields.io/github/stars/imsanghaar/Hackathon-0?style=social)](https://github.com/imsanghaar/Hackathon-0)

</div>
