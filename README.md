# 🤖 AI Employee System

> **A Local AI-Powered Task Automation System**  
> **By Imam Sanghaar Chandio & Qwen Code**

[![Status](https://img.shields.io/badge/status-complete-brightgreen)](https://github.com/imsanghaar/Hackathon-0)
[![Python](https://img.shields.io/badge/python-3.x-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

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

## 📖 What It Does

AI Employee System monitors folders for new files, automatically creates tasks, and integrates with AI agents (Claude, Gemini, Qwen) to process them:

```
📥 Inbox → 📝 Auto-Create Tasks → 🤖 AI Processing → ✅ Done
```

---

## 🏗️ Architecture

### Tier Structure

| Tier | Description | Status |
|------|-------------|--------|
| **Bronze** | Core CLI with file monitoring & task management | ✅ Complete |
| **Silver** | Scheduler daemon, human approval, task planning | ✅ Complete |

### System Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Inbox/     │ ──▶ │ Needs_Action/│ ──▶ │ AI Processing│ ──▶ │    Done/     │
│  (New Files) │     │  (Pending)   │     │  (External)  │     │  (Completed) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                                                            │
       ▼                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    File Watcher (5s interval)                               │
│                    Interactive CLI (Menu-driven)                            │
│                    Dashboard.md + System_Log.md (Auto-updated)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
Hackathon-0/
├── .claude/skills/          # AI Agent Skills (Process Tasks, Make Plan, etc.)
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

---

## 💻 Usage

### Main Commands

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

### AI Agent Workflow

1. Press `[3]` in CLI to start task processing
2. Open AI agent (Claude/Gemini/Qwen) in another terminal
3. Say **"Process Tasks"** to complete all pending tasks
4. Return to CLI and press Enter to refresh

---

## 🤖 Agent Skills

Agent Skills are documented behaviors for AI agents to interact with the vault system.

| Skill | Trigger | Action |
|-------|---------|--------|
| **Process Tasks** | `"Process Tasks"` | Complete tasks, update Dashboard & Log |
| **Make a Plan** | `"Make a Plan for tasks"` | Create strategic planning document |

Skills are located in `.claude/skills/` with detailed `SKILL.md` documentation.

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# AI API Keys
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### Intervals

| Setting | Default | Description |
|---------|---------|-------------|
| `CHECK_INTERVAL` | 2s | CLI refresh interval |
| `WATCH_INTERVAL` | 5s | File watcher interval |

---

## 🧪 Testing

```bash
# Run test suite
python scripts/test_implementations.py

# Check scheduler status
python scripts/run_ai_employee.py --status

# Single cycle test
python scripts/run_ai_employee.py --once
```

---

## 📄 Documentation

| Document | Description |
|----------|-------------|
| [Company_Handbook.md](Company_Handbook.md) | System guidelines |
| [Dashboard.md](Dashboard.md) | Current task overview |
| [System_Log.md](System_Log.md) | Activity history |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | MCP server setup |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - Feel free to use and modify! See [LICENSE](LICENSE) for details.

---

## 👥 Contributors

| Name | Role | Links |
|------|------|-------|
| **Imam Sanghaar Chandio** | Creator | [GitHub](https://github.com/imsanghaar) • [LinkedIn](https://www.linkedin.com/in/imam-sanghaar-chandio-96780b274) • [Portfolio](https://imsanghaar.vercel.app) |
| **Qwen Code** | AI Assistant | [Alibaba Cloud](https://www.alibabacloud.com/) |

---

## 🏆 Status

**Bronze Tier:** ✅ Complete  
**Silver Tier:** ✅ Complete

**Last Updated:** February 28, 2026

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Built with ❤️ by Imam Sanghaar Chandio & Qwen Code

[Report Bug](https://github.com/imsanghaar/Hackathon-0/issues) · [Request Feature](https://github.com/imsanghaar/Hackathon-0/issues)

</div>
