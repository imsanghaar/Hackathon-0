# 🤖 AI Employee System (Digital FTE)

> **A Full-Time Equivalent (FTE) Digital Employee Powered by AI**  
> An autonomous automation system that monitors communication channels, creates execution plans, and processes tasks using specialized AI Agent Skills—working 24/7 with human-in-the-loop oversight.

[![Status: Complete](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Tier: Silver](https://img.shields.io/badge/Tier-Silver-lightgrey?style=for-the-badge)](https://github.com/imsanghaar/Hackathon-0)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)](https://python.org)
[![MCP: Enabled](https://img.shields.io/badge/MCP-Enabled-orange?style=for-the-badge)](https://modelcontextprotocol.io/)

---

## 📑 Overview

The AI Employee System is a multi-tier automation framework designed to handle business workflows autonomously. From simple file monitoring to complex browser-based tasks like LinkedIn posting and Gmail management, the system operates through a modular "Agent Skill" architecture.

### Key Capabilities
- **Multi-Channel Monitoring:** Watches local folders and Gmail for new tasks.
- **Strategic Planning:** Automatically generates detailed `Plan.md` files for complex requests.
- **Browser Automation:** Uses Playwright MCP for LinkedIn posting and web-based actions.
- **Human-in-the-Loop:** Sensitive actions require explicit human approval via the vault.
- **Robust Scheduling:** Production-ready daemon with lock files and log rotation.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.8+
- Node.js (for MCP server)
- Chrome/Edge browser (for Playwright)

### 2. Clone and Install
```bash
git clone https://github.com/imsanghaar/Hackathon-0.git
cd Hackathon-0
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the template and fill in your credentials for Gmail and LinkedIn:
```bash
cp .env.example .env
# Edit .env with your specific details
```

---

## 🥉 Bronze Tier: Core Foundation

Focuses on the interactive CLI, local file monitoring, and basic task processing.

### Running Commands
| Component | Command |
| :--- | :--- |
| **Interactive CLI** | `python ai_employee.py` |
| **Inbox Watcher** | `python scripts/watch_inbox.py` |
| **Live Dashboard** | `python ai_employee.py --dashboard` |

---

## 🥈 Silver Tier: Advanced Automation

The Silver Tier introduces long-running background processes, external integrations, and strategic reasoning.

### 1. Start the MCP Server (Crucial)
The Silver Tier requires the Playwright MCP server for all browser-based operations:
```bash
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

### 2. Silver Tier Components & Running Commands

| Component | Description | Command |
| :--- | :--- | :--- |
| **Production Scheduler** | Runs the main autonomous loop (watcher + planner). | `python scripts/run_ai_employee.py --daemon` |
| **Gmail Watcher** | Monitors your inbox and creates tasks from new emails. | `python .claude/skills/gmail-watcher/scripts/watch_gmail.py --watch` |
| **LinkedIn Automator** | Handles automated posting to LinkedIn for lead generation. | `python .claude/skills/linkedin-post/scripts/linkedin_auto.py` |
| **Approval Checker** | Monitors the vault for human approvals/rejections. | `python scripts/requests-approval.py --timeout 7200` |
| **Task Planner** | Analyzes inbox and creates step-by-step Plan.md files. | `python scripts/task_planner.py` |

### 3. How to Run the Watchers

#### **Gmail Watcher**
The Gmail watcher uses Playwright to check your emails. It can run as a standalone service:
```bash
# Continuous monitoring every 5 minutes
python .claude/skills/gmail-watcher/scripts/watch_gmail.py --watch --interval 300
```

#### **LinkedIn Automator (Poster)**
While the scheduler can trigger it, you can run a post manually:
```bash
# Execute a LinkedIn post immediately
python .claude/skills/linkedin-post/scripts/linkedin_auto.py --text "Your post content here"
```

#### **Vault Inbox Watcher**
Monitors the `AI_Employee_Vault/Inbox` folder for new markdown files:
```bash
python scripts/watch_inbox.py
```

---

## 🛠️ Architecture: Agent Skills

All AI functionality is decoupled into "Skills" located in `.claude/skills/`. Each skill includes a `SKILL.md` defining its behavior and a Python script for execution.

| Skill | Purpose |
| :--- | :--- |
| `gmail-watcher` | Monitors Gmail for task-related emails. |
| `linkedin-post` | Automates LinkedIn content publishing. |
| `task-planner` | Creates step-by-step execution plans. |
| `human-approval` | Manages the approval/rejection workflow. |
| `vault-file-manager` | Handles file movements across tiers. |

---

## 📊 Documentation & Monitoring

- **[Dashboard.md](Dashboard.md):** Real-time overview of task statistics and system health.
- **[Company_Handbook.md](Company_Handbook.md):** Operational guidelines for the AI Employee.
- **[MCP_INTEGRATION.md](MCP_INTEGRATION.md):** Detailed guide for the Model Context Protocol setup.
- **[System_Log.md](System_Log.md):** Chronological log of all autonomous actions.

---

## 👨‍💻 Development Team

**Imam Sanghaar Chandio**  
*Lead Developer & Prompt Engineer*

- 📧 imamsanghaar@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274)
- 🌐 [GitHub](https://github.com/imsanghaar)

**AI Contributors**
- **Qwen Code:** Architecture & Logic Optimization
- **Claude Code:** Agent Skills & MCP Integration
- **Gemini CLI:** Final Verification, README Refinement & Deployment

---

<div align="center">

**⭐ Star this repo if you find it useful!**  
Built with ❤️ for the AI Automation Hackathon 2026.

</div>
