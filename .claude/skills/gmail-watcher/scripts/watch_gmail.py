#!/usr/bin/env python3
"""
Gmail Watcher - Monitor Gmail for new emails using Playwright MCP

Creates tasks in AI_Employee_Vault/Inbox/ for matching emails.

Usage:
    python watch_gmail.py                    # Check Gmail
    python watch_gmail.py --label "Important" # Specific label
    python watch_gmail.py --dry-run          # Preview only
    python watch_gmail.py --watch            # Continuous monitoring
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
BASE_DIR = SKILL_DIR.parent.parent

VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
LOGS_DIR = BASE_DIR / "Logs"

GMAIL_PROCESSED_FILE = LOGS_DIR / "gmail_processed.txt"
GMAIL_LOG_FILE = LOGS_DIR / "gmail_watcher.log"

MCP_SERVER_URL = "http://localhost:8808"

# =============================================================================
# MCP CLIENT
# =============================================================================

class MCPClient:
    """Simple MCP client for Playwright MCP server"""
    
    def __init__(self, url: str):
        self.url = url.rstrip('/')
        if not self.url.endswith('/mcp'):
            self.url = self.url + '/mcp'
        self._request_id = 0
        self._session_id = None
        self._initialized = False
    
    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    def _ensure_initialized(self):
        if self._initialized:
            return
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "gmail-watcher", "version": "1.0.0"}
            }
        }
        
        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        req = Request(self.url, data=data, headers=headers, method='POST')
        
        try:
            with urlopen(req, timeout=30) as resp:
                self._session_id = resp.headers.get('Mcp-Session-Id')
                response = self._parse_response(resp.read().decode('utf-8'))
        except Exception as e:
            raise Exception(f"Failed to initialize MCP: {e}")
        
        self._initialized = True
        self._send_notification("notifications/initialized")
    
    def _parse_response(self, body: str) -> dict:
        body = body.strip()
        if body.startswith('event:') or body.startswith('data:'):
            for line in body.split('\n'):
                if line.startswith('data:'):
                    json_data = line[5:].strip()
                    if json_data:
                        return json.loads(json_data)
            raise Exception("No data in SSE response")
        return json.loads(body)
    
    def _send_notification(self, method: str, params: dict = None):
        payload = {"jsonrpc": "2.0", "method": method}
        if params:
            payload["params"] = params
        
        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        
        req = Request(self.url, data=data, headers=headers, method='POST')
        try:
            with urlopen(req, timeout=10):
                pass
        except:
            pass
    
    def call_tool(self, tool_name: str, params: dict = None):
        self._ensure_initialized()
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": tool_name}
        }
        if params:
            payload["params"]["arguments"] = params
        
        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        
        req = Request(self.url, data=data, headers=headers, method='POST')
        
        try:
            with urlopen(req, timeout=30) as resp:
                response = self._parse_response(resp.read().decode('utf-8'))
        except Exception as e:
            raise Exception(f"MCP call failed: {e}")
        
        if "error" in response:
            err = response["error"]
            raise Exception(f"Tool error: {err.get('message')}")
        
        return response.get("result", {})


# =============================================================================
# GMAIL WATCHER
# =============================================================================

class GmailWatcher:
    """Monitor Gmail for new emails"""
    
    def __init__(self, label: str = None, dry_run: bool = False):
        self.label = label
        self.dry_run = dry_run
        self.mcp = MCPClient(MCP_SERVER_URL)
        self.processed_emails = self._load_processed()
        self.created_tasks = []
    
    def _load_processed(self) -> set:
        """Load list of processed email IDs"""
        try:
            if GMAIL_PROCESSED_FILE.exists():
                with open(GMAIL_PROCESSED_FILE, 'r') as f:
                    return set(line.strip() for line in f if line.strip())
        except:
            pass
        return set()
    
    def _save_processed(self, email_id: str):
        """Save email ID to processed list"""
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            with open(GMAIL_PROCESSED_FILE, 'a') as f:
                f.write(email_id + '\n')
        except:
            pass
    
    def _log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] {message}\n'
        print(log_entry.strip())
        
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            with open(GMAIL_LOG_FILE, 'a') as f:
                f.write(log_entry)
        except:
            pass
    
    def navigate_to_gmail(self):
        """Navigate to Gmail"""
        self._log("Navigating to Gmail...")
        self.mcp.call_tool("browser_navigate", {"url": "https://mail.google.com/mail/u/0/#inbox"})
        self.mcp.call_tool("browser_wait_for", {"time": 5000})

    def check_logged_in(self) -> bool:
        """Check if user is logged into Gmail"""
        try:
            snapshot = self.mcp.call_tool("browser_snapshot")
            # Check for Gmail interface elements like inbox count
            snapshot_text = str(snapshot)
            if "Inbox" in snapshot_text and ("unread" in snapshot_text.lower() or "mail.google.com" in snapshot_text):
                return True
            return False
        except:
            return False

    def get_unread_emails(self) -> list:
        """Get list of unread emails from Gmail snapshot"""
        self._log("Checking for unread emails...")

        try:
            # Navigate to inbox
            self.mcp.call_tool("browser_navigate", {"url": "https://mail.google.com/mail/u/0/#inbox"})
            self.mcp.call_tool("browser_wait_for", {"time": 3000})

            # Get snapshot to find emails
            snapshot = self.mcp.call_tool("browser_snapshot")
            snapshot_text = str(snapshot)
            
            # Parse snapshot for email rows
            # Gmail snapshot contains rows with format like:
            # row "unread, Sender Name, Subject, Time, Preview text.."
            emails = []
            
            # Find all email rows in snapshot
            lines = snapshot_text.split('\n')
            for line in lines:
                if 'row' in line.lower() and 'unread' in line.lower():
                    try:
                        # Extract email info from row
                        # Format: row "unread, Sender, Subject, Time, Preview"
                        parts = line.split(',')
                        if len(parts) >= 4:
                            sender = parts[1].strip().strip('"').strip()
                            subject = parts[2].strip().strip('"').strip()
                            
                            # Get time (usually 3rd or 4th element)
                            time_str = ""
                            for p in parts[3:5]:
                                p = p.strip().strip('"').strip()
                                if any(c.isdigit() for c in p) or ':' in p or 'AM' in p or 'PM' in p:
                                    time_str = p
                                    break
                            
                            # Get preview from remaining text
                            preview_parts = parts[4:] if len(parts) > 4 else parts[3:]
                            preview = ' '.join(p.strip().strip('"').strip() for p in preview_parts)[:200]
                            
                            # Create unique ID from subject+sender
                            email_id = f"{sender}_{subject}"[:100]
                            
                            emails.append({
                                "id": email_id,
                                "subject": subject if subject else "(No Subject)",
                                "from": sender if sender else "Unknown",
                                "date": time_str if time_str else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "preview": preview if preview else "No preview available"
                            })
                            
                            self._log(f"Found email: {subject} from {sender}")
                    except Exception as e:
                        self._log(f"Error parsing email row: {e}")
                        continue

            self._log(f"Found {len(emails)} unread emails")
            return emails

        except Exception as e:
            self._log(f"Error getting emails: {e}")
            return []
    
    def create_task(self, email: dict):
        """Create task file for email"""
        if email["id"] in self.processed_emails:
            self._log(f"Skipping already processed: {email['subject']}")
            return
        
        if self.dry_run:
            self._log(f"[DRY-RUN] Would create task for: {email['subject']}")
            return
        
        self._log(f"Creating task for: {email['subject']}")
        
        # Create task file
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        safe_subject = email["subject"].replace(' ', '_').replace('/', '_')[:50]
        task_filename = f"email_{safe_subject}_{timestamp.replace(' ', '_').replace(':', '')}.md"
        task_path = INBOX_DIR / task_filename
        
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        
        content = f"""---
type: email_task
status: new
priority: medium
created_at: {timestamp}
source: gmail
email_subject: "{email['subject']}"
email_from: "{email['from']}"
email_date: "{email['date']}"
---

# Email Task: {email['subject']}

## Email Details

- **From:** {email['from']}
- **Date:** {email['date']}
- **Subject:** {email['subject']}

## Email Preview

{email['preview']}

## Required Actions

- [ ] Review email content
- [ ] Prepare response or action
- [ ] Send response via email
- [ ] Update task status

---
*Created by Gmail Watcher*
"""
        
        with open(task_path, 'w') as f:
            f.write(content)
        
        self.created_tasks.append(task_filename)
        self._save_processed(email["id"])
        self._log(f"Created task: {task_filename}")
    
    def run(self):
        """Run the Gmail watcher"""
        self._log("=" * 60)
        self._log("GMAIL WATCHER - Starting")
        self._log("=" * 60)
        
        try:
            # Navigate to Gmail
            self.navigate_to_gmail()
            
            # Check if logged in
            if not self.check_logged_in():
                self._log("ERROR: Not logged into Gmail. Please log in manually.")
                self._log("TIP: Use browser in non-headless mode for first login.")
                return
            
            self._log("Successfully logged into Gmail")
            
            # Get unread emails
            emails = self.get_unread_emails()
            self._log(f"Found {len(emails)} unread emails")
            
            # Create tasks for new emails
            for email in emails:
                self.create_task(email)
            
            # Summary
            self._log("=" * 60)
            self._log(f"GMAIL WATCHER - Complete")
            self._log(f"Checked: {len(emails)} emails")
            self._log(f"Created: {len(self.created_tasks)} tasks")
            self._log("=" * 60)
            
        except Exception as e:
            self._log(f"ERROR: {e}")
            raise


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Gmail Watcher - Monitor Gmail for new emails')
    parser.add_argument('--label', '-l', help='Gmail label to check (default: Inbox)')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Preview without creating tasks')
    parser.add_argument('--watch', '-w', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    if args.watch:
        # Continuous monitoring
        print(f"Starting Gmail Watcher in continuous mode (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                watcher = GmailWatcher(label=args.label, dry_run=args.dry_run)
                watcher.run()
                
                import time
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nGmail Watcher stopped")
    else:
        # Single run
        watcher = GmailWatcher(label=args.label, dry_run=args.dry_run)
        watcher.run()


if __name__ == '__main__':
    main()
