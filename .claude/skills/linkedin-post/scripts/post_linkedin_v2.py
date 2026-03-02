#!/usr/bin/env python3
"""
LinkedIn Post - Robust Implementation

Uses multiple strategies to post to LinkedIn.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import time

# Auto-load .env file from project root
def load_env():
    """Load environment variables from .env file"""
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
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def create_linkedin_post(text: str) -> dict:
    """
    Create a LinkedIn post using browser automation.
    Uses multiple strategies and extended timeouts.
    """
    if not HAS_PLAYWRIGHT:
        return {'success': False, 'message': 'Playwright not installed'}
    
    email = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')
    
    if not email:
        return {'success': False, 'message': 'LINKEDIN_EMAIL not set'}
    if not password:
        return {'success': False, 'message': 'LINKEDIN_PASSWORD not set'}
    
    print(f"[*] Starting LinkedIn post automation...")
    print(f"[*] Email: {email}")
    
    try:
        with sync_playwright() as p:
            # Launch browser (headed for visibility)
            print("[*] Launching browser...")
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Step 1: Go to LinkedIn
            print("[*] Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/', wait_until='networkidle', timeout=60000)
            time.sleep(3)
            
            # Take screenshot
            try:
                page.screenshot(path='/tmp/li_step1.png')
                print("[*] Screenshot saved: /tmp/li_step1.png")
            except:
                pass
            
            # Step 2: Check if already logged in
            current_url = page.url
            print(f"[*] Current URL: {current_url}")
            
            if 'login' in current_url or 'checkpoint' in current_url:
                print("[*] Need to login...")
                # Login
                try:
                    page.fill('#username', email)
                    page.fill('#password', password)
                    time.sleep(1)
                    page.click('button[type="submit"]')
                    print("[*] Login submitted...")
                    page.wait_for_load_state('networkidle', timeout=30000)
                    time.sleep(5)
                except Exception as e:
                    print(f"[!] Login error: {e}")
            
            # Step 3: Navigate to feed
            print("[*] Navigating to feed...")
            page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
            time.sleep(5)
            
            # Screenshot
            try:
                page.screenshot(path='/tmp/li_step3.png')
            except:
                pass
            
            # Step 4: Find and click post button
            print("[*] Looking for post creation button...")
            
            # Strategy 1: Click the "Start a post" button
            clicked = False
            selectors = [
                'button:has-text("Start a post")',
                '.share-box-feed-entry__trigger',
                'button[aria-label*="post"]',
                'div[role="button"]:has-text("Start")',
            ]
            
            for selector in selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=5000):
                        print(f"[*] Found button with selector: {selector}")
                        btn.click()
                        clicked = True
                        time.sleep(2)
                        break
                except Exception as e:
                    print(f"[*] Selector failed: {selector} - {e}")
                    continue
            
            if not clicked:
                print("[!] Could not find post button")
                browser.close()
                return {'success': False, 'message': 'Could not find post button'}
            
            # Screenshot
            try:
                page.screenshot(path='/tmp/li_step4.png')
            except:
                pass
            
            # Step 5: Wait for dialog and type
            print("[*] Waiting for post dialog...")
            time.sleep(3)
            
            # Find editor
            editor_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[aria-label*="What do you want"]',
                'div[placeholder*="start a post"]',
            ]
            
            typed = False
            for selector in editor_selectors:
                try:
                    editor = page.locator(selector).first
                    if editor.is_visible(timeout=5000):
                        print(f"[*] Found editor with selector: {selector}")
                        editor.fill(text)
                        typed = True
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not typed:
                print("[!] Could not find editor")
                browser.close()
                return {'success': False, 'message': 'Could not find editor'}
            
            # Screenshot
            try:
                page.screenshot(path='/tmp/li_step5.png')
            except:
                pass
            
            # Step 6: Click Post button
            print("[*] Clicking Post button...")
            time.sleep(2)
            
            post_selectors = [
                'button:has-text("Post")',
                'button:has-text("post")',
            ]
            
            posted = False
            for selector in post_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_enabled(timeout=5000):
                        print(f"[*] Found post button: {selector}")
                        btn.click()
                        posted = True
                        time.sleep(3)
                        break
                except:
                    continue
            
            if not posted:
                print("[!] Could not find Post button")
                browser.close()
                return {'success': False, 'message': 'Could not find Post button'}
            
            # Screenshot
            try:
                page.screenshot(path='/tmp/li_step6.png')
            except:
                pass
            
            # Wait for confirmation
            print("[*] Waiting for post confirmation...")
            time.sleep(5)
            
            browser.close()
            
            print("[*] SUCCESS! Post should be published!")
            return {'success': True, 'message': 'Post published successfully'}
            
    except Exception as e:
        print(f"[!] Error: {e}")
        return {'success': False, 'message': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Post to LinkedIn')
    parser.add_argument('--text', required=True, help='Post content')
    args = parser.parse_args()
    
    result = create_linkedin_post(args.text)
    
    if result['success']:
        print(f"\n✅ SUCCESS: {result['message']}")
        sys.exit(0)
    else:
        print(f"\n❌ ERROR: {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
