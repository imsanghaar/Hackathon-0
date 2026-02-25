#!/usr/bin/env python3
"""
LinkedIn Post - Updated Login Selectors
"""

import os
import sys
from pathlib import Path
import time

def load_env():
    script_dir = Path(__file__).parent.resolve()
    for _ in range(5):
        env_file = script_dir / '.env'
        if env_file.exists():
            break
        script_dir = script_dir.parent
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

from playwright.sync_api import sync_playwright

email = os.environ.get('LINKEDIN_EMAIL')
password = os.environ.get('LINKEDIN_PASSWORD')
post_text = """🎉 Exciting Milestone Achieved! 🎉

I'm thrilled to announce that I have successfully completed both Bronze and Silver Tiers of Hackathon 0!

🥈 What I Built:
✅ Bronze Tier: Interactive AI Employee CLI with real-time dashboard, file monitoring, and task management
✅ Silver Tier: Production-ready scheduler with human approval workflow, automated task planning, and continuous monitoring

🔧 Technologies Used:
• Python 3.10+
• SMTP (Gmail API)
• Playwright for browser automation
• File system watchers
• Human-in-the-loop approval system

📚 Documentation:
Hackathon 0 Docs: https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0

This project demonstrates practical AI automation with real-world applications including email notifications, social media posting, file management, and approval workflows.

#Hackathon0 #AI #Automation #Python #Developer #Achievement #ArtificialIntelligence #Coding

---
⚙️ Automated Post | Agent: AI Employee System (Silver Tier) | Time: 11:48 | Date: 2026-02-25 | Posted from: E:\\ai_employee\\[Bronze_Tier](Silver_Tier)"""

print("=" * 60)
print("LINKEDIN AUTO-POSTER v3")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Go directly to login page
    print("\n[1] Going to login page...")
    page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=60000)
    time.sleep(5)
    page.screenshot(path='/tmp/li_login_page.png')
    print(f"    URL: {page.url}")
    
    # Try multiple login selectors
    print("[2] Logging in...")
    login_selectors = [
        ('#username', '#password', 'button[type="submit"]'),
        ('#session_key', '#session_password', 'button[type="submit"]'),
        ('input[name="session_key"]', 'input[name="session_password"]', 'button[type="submit"]'),
        ('#email', '#password', 'input[type="submit"]'),
    ]
    
    logged_in = False
    for user_sel, pass_sel, btn_sel in login_selectors:
        try:
            print(f"    Trying: {user_sel} + {pass_sel}")
            if page.is_visible(user_sel, timeout=3000):
                page.fill(user_sel, email)
                page.fill(pass_sel, password)
                time.sleep(2)
                page.click(btn_sel)
                page.wait_for_load_state('networkidle', timeout=30000)
                time.sleep(5)
                
                if 'feed' in page.url or 'mynetwork' in page.url:
                    print("    ✓ Login successful!")
                    logged_in = True
                    break
        except Exception as e:
            print(f"    Failed: {e}")
            continue
    
    if not logged_in:
        print("    ❌ Login failed - check credentials")
        try:
            page.screenshot(path='/tmp/li_login_failed.png', timeout=5000)
        except:
            pass
        browser.close()
        sys.exit(1)
    
    try:
        page.screenshot(path='/tmp/li_logged_in.png', timeout=5000)
    except:
        pass
    
    # Go to feed
    print("[3] Going to feed...")
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(8)
    try:
        page.screenshot(path='/tmp/li_feed.png', timeout=5000)
    except:
        pass
    
    # Find post button
    print("[4] Finding post button...")
    post_btn_selectors = [
        'button:has-text("Start a post")',
        '.share-box-feed-entry__trigger',
        'button[aria-label*="post"]',
        '[data-control-name="update_posts"]',
    ]
    
    for sel in post_btn_selectors:
        try:
            if page.is_visible(sel, timeout=5000):
                print(f"    Found: {sel}")
                page.click(sel)
                time.sleep(5)
                try:
                    page.screenshot(path='/tmp/li_dialog.png', timeout=5000)
                except:
                    pass
                print("    ✓ Dialog opened!")
                break
        except Exception as e:
            print(f"    Selector failed: {e}")
            continue
    
    # Type post
    print("[5] Typing post...")
    time.sleep(3)
    editor_selectors = [
        'div[role="textbox"][contenteditable="true"]',
        'div[aria-label*="What do you want"]',
        'div[placeholder*="post"]',
    ]
    
    for sel in editor_selectors:
        try:
            editor = page.locator(sel).first
            if editor.is_visible(timeout=5000):
                editor.fill(post_text)
                time.sleep(3)
                print("    ✓ Content entered!")
                break
        except Exception as e:
            print(f"    Editor failed: {e}")
            continue
    
    try:
        page.screenshot(path='/tmp/li_content.png', timeout=5000)
    except:
        pass
    
    # Click Post
    print("[6] Publishing...")
    time.sleep(3)
    try:
        post_btn = page.locator('button:has-text("Post")').first
        if post_btn.is_enabled(timeout=5000):
            post_btn.click()
            time.sleep(8)
            try:
                page.screenshot(path='/tmp/li_published.png', timeout=5000)
            except:
                pass
            print("    ✓ Post button clicked!")
        else:
            print("    Post button not enabled")
    except Exception as e:
        print(f"    ❌ Could not click Post: {e}")
    
    browser.close()
    print("\n" + "=" * 60)
    print("DONE! Check /tmp/li_*.png for screenshots")
    print("=" * 60)
