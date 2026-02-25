#!/usr/bin/env python3
"""
LinkedIn Post - Production Ready

Create real LinkedIn posts using Playwright browser automation.
Requires LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables.

Usage:
    python post_linkedin.py --text "Your post content here"
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

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

# Load .env before anything else
load_env()

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def create_linkedin_post(text: str, headless: bool = True) -> dict:
    """
    Create a LinkedIn post using browser automation.
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    if not HAS_PLAYWRIGHT:
        return {'success': False, 'message': 'Playwright not installed. Run: pip install playwright'}
    
    email = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')
    
    if not email:
        return {'success': False, 'message': 'LINKEDIN_EMAIL not set in environment'}
    
    if not password:
        return {'success': False, 'message': 'LINKEDIN_PASSWORD not set in environment'}
    
    if not text or len(text.strip()) == 0:
        return {'success': False, 'message': 'Post text cannot be empty'}
    
    if len(text) > 3000:
        return {'success': False, 'message': 'Post text exceeds 3000 character limit'}
    
    try:
        with sync_playwright() as p:
            # Launch browser - use headed mode for debugging
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Navigate to LinkedIn login
            page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=30000)
            
            # Save a screenshot for debugging
            try:
                page.screenshot(path='/tmp/linkedin_login.png')
            except:
                pass
            
            # Login
            try:
                page.fill('#username', email)
                page.fill('#password', password)
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
            except PlaywrightTimeout:
                browser.close()
                return {'success': False, 'message': 'Login failed - timeout waiting for page'}
            
            # Check if login was successful
            if 'login' in page.url:
                browser.close()
                return {'success': False, 'message': 'Login failed - check credentials'}
            
            # Navigate to homepage
            page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            
            # Wait for page to fully load
            page.wait_for_timeout(3000)
            
            # Find and click the post creation box
            try:
                # Try multiple selectors for "Start a post" button
                post_button_selectors = [
                    'button:has-text("Start a post")',
                    'button:has-text("Starta post")',
                    '.share-box-feed-entry__trigger',
                    'div[role="button"]:has-text("Start")',
                    '[data-control-name="update_posts"]',
                    '.artdeco-button:has-text("Start")'
                ]
                
                clicked = False
                for selector in post_button_selectors:
                    try:
                        if page.locator(selector).first.is_visible(timeout=5000):
                            page.locator(selector).first.click(timeout=5000)
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    # Try clicking the avatar/profile area near the post box
                    try:
                        page.click('div[id="mupdate"]', timeout=5000)
                        clicked = True
                    except:
                        pass
                
                if not clicked:
                    browser.close()
                    return {'success': False, 'message': 'Could not find post creation button - LinkedIn UI may have changed'}
                    
            except Exception as e:
                browser.close()
                return {'success': False, 'message': f'Could not find post creation button: {str(e)}'}
            
            # Wait for post dialog to appear
            try:
                page.wait_for_selector('div[role="dialog"]', timeout=10000)
            except PlaywrightTimeout:
                # Dialog might not use role="dialog" - try other selectors
                try:
                    page.wait_for_selector('div[aria-label*="Create a post"]', timeout=5000)
                except PlaywrightTimeout:
                    # Just wait a bit and proceed - the click might have opened it
                    page.wait_for_timeout(2000)
            
            # Find the text editor and type the post
            try:
                # Try multiple selectors for the post editor
                editor_selectors = [
                    'div[role="textbox"][contenteditable="true"]',
                    'div[aria-label*="What do you want"]',
                    'div[placeholder*="What do you want"]',
                    '.editable-container',
                    'div[contenteditable="true"]'
                ]
                
                typed = False
                for selector in editor_selectors:
                    try:
                        editor = page.locator(selector).first
                        if editor.is_visible(timeout=3000):
                            editor.fill(text)
                            typed = True
                            break
                    except:
                        continue
                
                if not typed:
                    browser.close()
                    return {'success': False, 'message': 'Could not find post editor'}
                    
            except Exception as e:
                browser.close()
                return {'success': False, 'message': f'Could not find post editor: {str(e)}'}
            
            # Click the Post button
            try:
                post_button = page.locator('button:has-text("Post"), button:has-text("post")').first
                post_button.click(timeout=10000)
                
                # Wait for confirmation
                page.wait_for_load_state('networkidle')
            except PlaywrightTimeout:
                browser.close()
                return {'success': False, 'message': 'Failed to publish post'}
            
            browser.close()
            
            # Log the post
            log_post_created(text)
            
            return {'success': True, 'message': 'Post published successfully on LinkedIn'}
            
    except Exception as e:
        error_msg = str(e)
        if 'Authentication' in error_msg or 'credentials' in error_msg.lower():
            return {'success': False, 'message': 'LinkedIn authentication failed'}
        return {'success': False, 'message': f'Failed to create post: {error_msg}'}


def log_post_created(text: str) -> None:
    """Log created post to file"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, '..', '..', '..', 'Logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'linkedin_posts.log')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        preview = text[:100] + '...' if len(text) > 100 else text
        
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] Preview: {preview}\n')
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description='Create LinkedIn post')
    parser.add_argument('--text', required=True, help='Post content (max 3000 chars)')
    parser.add_argument('--visible', action='store_true', help='Show browser (not headless)')
    
    args = parser.parse_args()
    
    result = create_linkedin_post(args.text, headless=not args.visible)
    
    if result['success']:
        print(f"SUCCESS: {result['message']}")
        sys.exit(0)
    else:
        print(f"ERROR: {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
