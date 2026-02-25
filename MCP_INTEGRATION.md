# MCP Integration Guide

**AI Employee System - Silver Tier**

This document describes how the AI Employee System integrates with MCP (Model Context Protocol) servers for external actions.

---

## Overview

The AI Employee System uses **Playwright MCP** for browser automation tasks including:
- LinkedIn posting
- Gmail monitoring
- Web form filling
- Data extraction

---

## MCP Server Setup

### Playwright MCP Server

**Installation:**
```bash
npx @playwright/mcp@latest
```

**Start Server:**
```bash
# Start with shared browser context (recommended)
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

**Stop Server:**
```bash
# Close browser and stop server
pkill -f "@playwright/mcp"
```

**Verify Server:**
```bash
python claude-code-skills-lab-main/.claude/skills/browsing-with-playwright/scripts/mcp-client.py \
  list --url http://localhost:8808
```

---

## Available MCP Tools

### Browser Navigation

| Tool | Description | Parameters |
|------|-------------|------------|
| `browser_navigate` | Navigate to URL | `url` |
| `browser_navigate_back` | Go back in history | - |
| `browser_snapshot` | Get page accessibility snapshot | - |
| `browser_take_screenshot` | Take page screenshot | `type`, `fullPage` |

### Browser Interaction

| Tool | Description | Parameters |
|------|-------------|------------|
| `browser_click` | Click element | `element`, `ref` |
| `browser_type` | Type text | `element`, `ref`, `text`, `submit` |
| `browser_fill_form` | Fill multiple fields | `fields` |
| `browser_select_option` | Select dropdown option | `element`, `ref`, `values` |
| `browser_hover` | Hover over element | `element`, `ref` |

### Browser Wait & Execute

| Tool | Description | Parameters |
|------|-------------|------------|
| `browser_wait_for` | Wait for text/time | `text`, `textGone`, `time` |
| `browser_evaluate` | Execute JavaScript | `function` |
| `browser_run_code` | Run Playwright code | `code` |

---

## Using MCP in Skills

### Example: LinkedIn Posting

```python
from mcp_client import MCPClient

mcp = MCPClient("http://localhost:8808")

# Navigate to LinkedIn
mcp.call_tool("browser_navigate", {"url": "https://linkedin.com"})

# Wait for page load
mcp.call_tool("browser_wait_for", {"time": 3000})

# Get snapshot to find elements
snapshot = mcp.call_tool("browser_snapshot")

# Click "Start a post" button
mcp.call_tool("browser_click", {
    "element": "Start a post button",
    "ref": "e42"
})

# Type post content
mcp.call_tool("browser_type", {
    "element": "Post editor",
    "ref": "e55",
    "text": "Exciting news! #hackathon"
})

# Click Post button
mcp.call_tool("browser_click", {
    "element": "Post button",
    "ref": "e60"
})
```

### Example: Gmail Monitoring

```python
from mcp_client import MCPClient

mcp = MCPClient("http://localhost:8808")

# Navigate to Gmail
mcp.call_tool("browser_navigate", {"url": "https://mail.google.com"})

# Wait for inbox to load
mcp.call_tool("browser_wait_for", {"time": 3000})

# Get snapshot
snapshot = mcp.call_tool("browser_snapshot")

# Extract email information from snapshot
# Parse and create tasks
```

---

## Skills Using MCP

### 1. LinkedIn Post Skill

**Location:** `.claude/skills/linkedin-post/`

**Uses MCP for:**
- Browser navigation
- Post dialog interaction
- Content entry
- Post submission

**Script:** `linkedin_auto.py`

---

### 2. Gmail Watcher Skill

**Location:** `.claude/skills/gmail-watcher/`

**Uses MCP for:**
- Gmail navigation
- Inbox monitoring
- Email extraction
- Unread status checking

**Script:** `watch_gmail.py`

---

## MCP Client Usage

### List Available Tools

```bash
python mcp-client.py list --url http://localhost:8808
```

### Call a Tool

```bash
python mcp-client.py call \
  --url http://localhost:8808 \
  --tool browser_navigate \
  --params '{"url": "https://example.com"}'
```

### Emit Tool Documentation

```bash
python mcp-client.py emit \
  --url http://localhost:8808 \
  --format markdown
```

---

## Configuration

### Environment Variables

Add to `.env`:

```env
# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8808
MCP_TIMEOUT=30
MCP_SHARED_CONTEXT=true
```

### Server Auto-Start

Create helper script `start_mcp.sh`:

```bash
#!/bin/bash
# Check if MCP server is running
if ! pgrep -f "@playwright/mcp" > /dev/null; then
    echo "Starting Playwright MCP server..."
    npx @playwright/mcp@latest --port 8808 --shared-browser-context &
    sleep 5
    echo "Server started on port 8808"
else
    echo "MCP server already running"
fi
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
netstat -an | grep 8808

# Kill existing process
pkill -f "@playwright/mcp"

# Restart server
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

### Tool Call Fails

1. **Check server is running:**
   ```bash
   curl http://localhost:8808/mcp
   ```

2. **Verify tool name:**
   ```bash
   python mcp-client.py list --url http://localhost:8808
   ```

3. **Check parameters:**
   - Ensure JSON is valid
   - Verify required fields

### Browser Context Lost

**Problem:** Each call gets fresh browser state

**Solution:** Use `--shared-browser-context` flag:
```bash
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

### Login Session Lost

**Problem:** Gmail/LinkedIn requires login every time

**Solutions:**
1. Use browser profile with saved session
2. Use `.browser_profile` directory for persistent cookies
3. Login once and keep server running

---

## Best Practices

### 1. Server Lifecycle

- **Start:** Before browser automation tasks
- **Keep Running:** For multiple related operations
- **Stop:** When all browser work is complete

### 2. Error Handling

```python
try:
    result = mcp.call_tool("browser_navigate", {"url": "https://..."})
except Exception as e:
    log_error(f"Navigation failed: {e}")
    return False
```

### 3. Rate Limiting

- Wait 2-3 seconds between actions
- Use `browser_wait_for` for page loads
- Don't spam tool calls

### 4. Element References

- Always get fresh snapshot before interacting
- Element refs change on each snapshot
- Store refs temporarily for multi-step operations

---

## Security Notes

- **Never** store credentials in code
- Use environment variables for sensitive data
- MCP server runs locally - no external exposure
- Browser sessions are isolated per server instance

---

## Future Enhancements

### Planned MCP Integrations

1. **Gmail MCP Server** - Direct Gmail API access
2. **Filesystem MCP** - Enhanced file operations
3. **Database MCP** - SQL database access
4. **Calendar MCP** - Google Calendar integration

### Custom MCP Server

Create `mcp_server.py` for AI Employee actions:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("ai-employee")

@server.tool("send_email")
async def send_email(to: str, subject: str, body: str):
    # Call gmail-send skill
    ...

@server.tool("post_linkedin")
async def post_linkedin(text: str):
    # Use Playwright MCP
    ...

async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream)
```

---

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

**Last Updated:** February 25, 2026
**Version:** 1.0
