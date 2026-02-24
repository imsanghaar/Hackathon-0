# Hackathon 0 - Bronze Tier

## Bronze Tier: Foundation (Minimum Viable Deliverable)

**Estimated Time:** 8-12 hours

**Deliverables:**
- Obsidian vault with Dashboard.md and Company_Handbook.md
- One working Watcher script (file system monitoring)
- Claude Code successfully reading from and writing to the vault
- Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- All AI functionality implemented as Agent Skills

---

## 1. What Is It?

This project is a **Local AI Employee System** built on a structured vault system. It acts as an intelligent assistant that monitors folders, creates tasks, and manages workflows automatically. The system is designed to be clean, modular, and production-ready while remaining beginner-friendly.

The Bronze Tier represents the **foundation layer** - a minimum viable product that demonstrates core functionality including file monitoring, task creation, and AI-driven task processing.

---

## 2. Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.x |
| File Monitoring | `pathlib`, `time` |
| Data Format | Markdown with YAML frontmatter |
| Vault Structure | Obsidian-compatible folders |
| AI Integration | Claude Code (via API) |
| External Dependencies | None (stdlib only) |

---

## 3. How Does It Work?

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Inbox     │────▶│ Needs_Action │────▶│    Done     │
│  (New Files)│     │   (Tasks)    │     │ (Completed) │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────┐
│              File Watcher (Monitors Inbox)          │
│              AI Agent (Processes Tasks)             │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              Dashboard.md (Status Overview)         │
│              System_Log.md (Activity Tracking)      │
│              Company_Handbook.md (Rules & Guidelines)│
└─────────────────────────────────────────────────────┘
```

### Workflow:
1. **File Watcher** monitors the `Inbox/` folder every 5 seconds
2. When a new file appears, a **task file** is created in `Needs_Action/`
3. User triggers **"Process Tasks"** command
4. AI reads tasks, completes them, moves files to `Done/`
5. Dashboard and System Log are updated automatically

---

## 4. Features

### Core Features
- **Automatic File Monitoring** - Watches Inbox for new files
- **Task Generation** - Creates structured task files with metadata
- **Duplicate Prevention** - Tracks processed files to avoid duplicates
- **Error Handling** - Graceful failure with error logging
- **Log Rotation** - Prevents log files from growing too large

### Agent Skills
| Skill | Trigger | Action |
|-------|---------|--------|
| Process Tasks | "Process Tasks" | Completes all pending tasks, updates Dashboard & Log |
| Make a Plan | "Make a Plan for tasks" | Creates planning document with task analysis |

### Folder Structure
```
bronze_tier/
├── Inbox/              # New files dropped here
├── Needs_Action/       # Pending task files
├── DOne/               # Completed tasks
├── Logs/               # System logs and error tracking
├── Plans/              # Planning documents and templates
├── Dashboard.md        # Task overview and status
├── Company_Handbook.md # Rules and guidelines
├── System_Log.md       # Activity log
├── file_watcher.py     # File monitoring script
└── log_manager.py      # Log rotation script
```

---

## 5. What Can It Do After Upgrade?

### Bronze Tier - Upgraded Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Watcher (Safe + Structured)** | Robust file monitoring with error handling, duplicate prevention, and structured task creation |
| 2 | **Qwen Task Processor** | AI-powered task processing using Qwen Code (Claude alternative) for reading, analyzing, and completing tasks |
| 3 | **Professional Task Templates** | Standardized task files with YAML frontmatter (type, status, priority, related_files) and clear checklists |
| 4 | **Smart Logging System** | Auto-rotating logs, error tracking, and activity history with size management |
| 5 | **Planning Ability (Silver Bridge)** | AI generates strategic planning documents analyzing pending tasks, priorities, and execution order |

### Silver Tier (Planned)
- **Reasoning Abilities** - AI analyzes tasks before executing
- **Smart Prioritization** - Auto-prioritize tasks based on content
- **Multi-Source Input** - Email (Gmail) integration
- **Advanced Planning** - Dependency tracking between tasks
- **Natural Language Commands** - More flexible trigger phrases

### Gold Tier (Future)
- **Autonomous Decision Making** - AI makes judgment calls on routine tasks
- **Cross-Platform Sync** - Sync vault across devices
- **Custom Watchers** - Pluggable watcher modules (API, webhooks, etc.)
- **Analytics Dashboard** - Visual charts and productivity metrics
- **Voice Commands** - Voice-activated task management

---

## Completion Status

**Bronze Tier of Hackathon Zero is COMPLETED**

**Completion Date:** Tuesday, February 24, 2026

**Delivered:**
- ✅ Obsidian vault structure with all required folders
- ✅ Dashboard.md, Company_Handbook.md, System_Log.md
- ✅ Working file_watcher.py with error handling
- ✅ log_manager.py for log rotation
- ✅ Agent Skills: "Process Tasks" and "Make a Plan for tasks"
- ✅ Claude Code integration (read/write to vault)
- ✅ Structured task templates with YAML frontmatter

---

## Developer

**Imam Sanghaar Chandio**  
*Prompt Engineer, Web Developer*  
Developer of this Local AI System
