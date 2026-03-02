#!/usr/bin/env python3
"""
LinkedIn Auto-Post - Automatically post to LinkedIn from task requests

Scans Needs_Action/ for LinkedIn post requests and posts automatically.

Usage:
    python auto_post.py              # Check and post
    python auto_post.py --dry-run    # Preview only
    python auto_post.py --watch      # Continuous monitoring
"""

import os
import sys
import argparse
import json
import time
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
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

LINKEDIN_LOG_FILE = LOGS_DIR / "linkedin_posts.log"
LINKEDIN_PROCESSED_FILE = LOGS_DIR / "linkedin_processed.txt"

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
                "clientInfo": {"name": "linkedin-auto-post", "version": "1.0.0"}
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
# LINKEDIN AUTO-POSTER
# =============================================================================

class LinkedInAutoPoster:
    """Automatically post to LinkedIn from task requests"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.mcp = MCPClient(MCP_SERVER_URL)
        self.processed_posts = self._load_processed()
        self.posts_created = 0
    
    def _load_processed(self) -> set:
        """Load list of processed post files"""
        try:
            if LINKEDIN_PROCESSED_FILE.exists():
                with open(LINKEDIN_PROCESSED_FILE, 'r') as f:
                    return set(line.strip() for line in f if line.strip())
        except:
            pass
        return set()
    
    def _save_processed(self, filename: str):
        """Save filename to processed list"""
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            with open(LINKEDIN_PROCESSED_FILE, 'a') as f:
                f.write(filename + '\n')
        except:
            pass
    
    def _log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] {message}\n'
        print(log_entry.strip())
        
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            with open(LINKEDIN_LOG_FILE, 'a') as f:
                f.write(log_entry)
        except:
            pass
    
    def find_linkedin_requests(self) -> list:
        """Find LinkedIn post request files in Needs_Action/"""
        requests = []
        
        if not NEEDS_ACTION_DIR.exists():
            return requests
        
        for file in NEEDS_ACTION_DIR.glob("*.md"):
            try:
                content = file.read_text()
                
                # Check if it's a LinkedIn post request
                if 'type: linkedin_post' in content.lower() or 'linkedin' in file.name.lower():
                    if file.name not in self.processed_posts:
                        requests.append(file)
                        self._log(f"Found LinkedIn post request: {file.name}")
            except:
                continue
        
        return requests
    
    def parse_post_request(self, file_path: Path) -> dict:
        """Parse LinkedIn post request file"""
        content = file_path.read_text()
        
        post_data = {
            "filename": file_path.name,
            "content": "",
            "hashtags": [],
            "priority": "medium"
        }
        
        # Extract frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                body = parts[2].strip()
                
                # Parse frontmatter
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'priority':
                            post_data['priority'] = value
                
                # Extract post content from body
                if '## Post Content' in body:
                    content_part = body.split('## Post Content')[1]
                    if '##' in content_part:
                        content_part = content_part.split('##')[0]
                    post_data['content'] = content_part.strip()
                elif '# LinkedIn Post' in body:
                    content_part = body.split('# LinkedIn Post')[1]
                    if '##' in content_part:
                        content_part = content_part.split('##')[0]
                    post_data['content'] = content_part.strip()
                else:
                    # Use entire body as content
                    post_data['content'] = body.strip()
                
                # Extract hashtags
                if '## Hashtags' in body:
                    hashtag_part = body.split('## Hashtags')[1]
                    if '##' in hashtag_part:
                        hashtag_part = hashtag_part.split('##')[0]
                    post_data['hashtags'] = [h.strip() for h in hashtag_part.split() if h.startswith('#')]
        
        return post_data
    
    def post_to_linkedin(self, post_content: str) -> bool:
        """Post content to LinkedIn using MCP"""
        try:
            self._log("Navigating to LinkedIn...")
            
            # Navigate to LinkedIn
            self.mcp.call_tool("browser_navigate", {"url": "https://www.linkedin.com/feed/"})
            time.sleep(3)
            
            # Click "Start a post"
            self._log("Opening post dialog...")
            self.mcp.call_tool("browser_click", {
                "element": "Start a post button",
                "ref": "e185"  # This may need to be updated based on actual snapshot
            })
            time.sleep(2)
            
            # Type post content
            self._log("Entering post content...")
            self.mcp.call_tool("browser_type", {
                "element": "Text editor for creating content",
                "ref": "e827",  # This may need to be updated
                "text": post_content[:3000]  # LinkedIn character limit
            })
            time.sleep(2)
            
            # Click Post button
            self._log("Publishing post...")
            self.mcp.call_tool("browser_click", {
                "element": "Post button",
                "ref": "e894"  # This may need to be updated
            })
            time.sleep(3)
            
            self._log("Post published successfully!")
            return True
            
        except Exception as e:
            self._log(f"Error posting to LinkedIn: {e}")
            return False
    
    def move_to_done(self, filename: str):
        """Move processed file to Done folder"""
        try:
            source = NEEDS_ACTION_DIR / filename
            dest = DONE_DIR / filename
            
            if source.exists():
                DONE_DIR.mkdir(parents=True, exist_ok=True)
                source.rename(dest)
                self._log(f"Moved {filename} to Done/")
        except Exception as e:
            self._log(f"Error moving file: {e}")
    
    def run(self):
        """Run the LinkedIn auto-poster"""
        self._log("=" * 60)
        self._log("LINKEDIN AUTO-POSTER - Starting")
        self._log("=" * 60)
        
        try:
            # Find LinkedIn post requests
            requests = self.find_linkedin_requests()
            self._log(f"Found {len(requests)} pending post request(s)")
            
            # Process each request
            for request_file in requests:
                self._log(f"\nProcessing: {request_file.name}")
                
                # Parse the request
                post_data = self.parse_post_request(request_file)
                self._log(f"Content: {post_data['content'][:100]}...")
                
                if self.dry_run:
                    self._log(f"[DRY-RUN] Would post: {post_data['content'][:100]}...")
                    self._save_processed(request_file.name)
                    continue
                
                # Post to LinkedIn
                success = self.post_to_linkedin(post_data['content'])
                
                if success:
                    self.posts_created += 1
                    self._save_processed(request_file.name)
                    self.move_to_done(request_file.name)
                else:
                    self._log(f"Failed to post: {request_file.name}")
            
            # Summary
            self._log("=" * 60)
            self._log(f"LINKEDIN AUTO-POSTER - Complete")
            self._log(f"Processed: {len(requests)} requests")
            self._log(f"Posted: {self.posts_created} posts")
            self._log("=" * 60)
            
        except Exception as e:
            self._log(f"ERROR: {e}")
            raise


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Poster')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Preview without posting')
    parser.add_argument('--watch', '-w', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    if args.watch:
        print(f"Starting LinkedIn Auto-Poster in continuous mode (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                poster = LinkedInAutoPoster(dry_run=args.dry_run)
                poster.run()
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nLinkedIn Auto-Poster stopped")
    else:
        poster = LinkedInAutoPoster(dry_run=args.dry_run)
        poster.run()


if __name__ == '__main__':
    main()
