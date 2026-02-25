#!/usr/bin/env python3
"""
LinkedIn Post - Final Robust Implementation

Handles login, navigation, and posting with extensive debugging.
"""

import os
import sys
import argparse
from datetime import datetime
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

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def post_to_linkedin(text: str):
    if not HAS_PLAYWRIGHT:
        print("❌ Playwright not installed")
        return False
    
    email = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Missing credentials in .env")
        return False
    
    print("=" * 60)
    print("LINKEDIN AUTO-POSTER")
    print("=" * 60)
    print(f"User: {email}")
    print(f"Post length: {len(text)} chars")
    print("=" * 60)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=2000)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            # Go to LinkedIn
            print("\n[1/6] Going to LinkedIn...")
            page.goto('https://www.linkedin.com/', wait_until='networkidle', timeout=60000)
            time.sleep(5)
            page.screenshot(path='/tmp/li_1_home.png')
            
            # Check URL
            url = page.url
            print(f"     URL: {url}")
            
            # Login if needed
            if 'login' in url or 'checkpoint' in url or '/feed' not in url:
                print("[2/6] Logging in...")
                try:
                    page.fill('#username', email)
                    page.fill('#password', password)
                    time.sleep(2)
                    page.click('button[type="submit"]')
                    page.wait_for_load_state('networkidle', timeout=30000)
                    time.sleep(5)
                    page.screenshot(path='/tmp/li_2_logged.png')
                    print("     Login complete!")
                except Exception as e:
                    print(f"     Login error: {e}")
            else:
                print("[2/6] Already logged in!")
            
            # Go to feed
            print("[3/6] Going to feed...")
            page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
            time.sleep(5)
            page.screenshot(path='/tmp/li_3_feed.png')
            print(f"     Current URL: {page.url}")
            
            # Find post button - try MANY selectors
            print("[4/6] Finding post button...")
            clicked = False
            
            # Extended list of selectors
            selectors = [
                'button:has-text("Start a post")',
                'button:has-text("Start")',
                '.share-box-feed-entry__trigger',
                '[data-control-name="update_posts"]',
                'button[aria-label*="post"]',
                'div[role="button"]:has-text("Start")',
                '.artdeco-button:has-text("Start")',
                'button:has-text("Create")',
            ]
            
            for sel in selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=3000):
                        print(f"     Found: {sel}")
                        btn.click()
                        clicked = True
                        time.sleep(3)
                        break
                except:
                    pass
            
            if not clicked:
                print("     ❌ Could not find post button")
                print("     Screenshots saved to /tmp/li_*.png")
                browser.close()
                return False
            
            page.screenshot(path='/tmp/li_4_dialog.png')
            print("     Post dialog opened!")
            
            # Type the post
            print("[5/6] Typing post content...")
            time.sleep(2)
            
            # Find editor
            editors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[aria-label*="What do you want"]',
                'div[placeholder*="post"]',
                '.editable-container',
            ]
            
            typed = False
            for sel in editors:
                try:
                    editor = page.locator(sel).first
                    if editor.is_visible(timeout=3000):
                        print(f"     Found editor: {sel}")
                        editor.fill(text)
                        typed = True
                        time.sleep(3)
                        break
                except:
                    pass
            
            if not typed:
                print("     ❌ Could not find editor")
                browser.close()
                return False
            
            page.screenshot(path='/tmp/li_5_typing.png')
            print("     Content entered!")
            
            # Click Post button
            print("[6/6] Publishing post...")
            time.sleep(2)
            
            post_btns = [
                'button:has-text("Post")',
                'button:has-text("post")',
                'button[data-control-name*="post"]',
            ]
            
            posted = False
            for sel in post_btns:
                try:
                    btn = page.locator(sel).first
                    if btn.is_enabled(timeout=3000):
                        print(f"     Found post button: {sel}")
                        btn.click()
                        posted = True
                        time.sleep(5)
                        break
                except:
                    pass
            
            page.screenshot(path='/tmp/li_6_done.png')
            
            if not posted:
                print("     ❌ Could not click Post button")
                browser.close()
                return False
            
            browser.close()
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Post published to LinkedIn!")
            print("=" * 60)
            print(f"Screenshots: /tmp/li_*.png")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', required=True, help='Post content')
    args = parser.parse_args()
    
    success = post_to_linkedin(args.text)
    sys.exit(0 if success else 1)
