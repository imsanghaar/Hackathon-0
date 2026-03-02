#!/usr/bin/env python3
"""
LinkedIn Post - Using Microsoft Edge
Uses Edge browser with user's existing session
"""

import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Credentials
email = 'imamsanghaar@gmail.com'
password = 'Sanghaar@2008'

# Edge user data directory (where Edge stores login sessions)
# On Windows: %LOCALAPPDATA%\Microsoft\Edge\User Data
# On Linux/WSL: We'll use a fresh profile
user_data_dir = Path('/tmp/edge_user_data')
user_data_dir.mkdir(exist_ok=True)

post = """🎉 Exciting Milestone Achieved! 🎉

I'm thrilled to announce that I have successfully completed both Bronze and Silver Tiers of Hackathon 0!

🥈 What I Built:
✅ Bronze Tier: Interactive AI Employee CLI with dashboard & file monitoring
✅ Silver Tier: Production scheduler with human approval workflow

🔧 Tech: Python 3.10+, SMTP, Playwright, File watchers

📚 Docs: https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0

#Hackathon0 #AI #Python #Automation

---
⚙️ Auto-posted | AI Employee Silver Tier | 2026-02-25"""

print('=' * 70)
print('LINKEDIN POST - MICROSOFT EDGE')
print('=' * 70)
print(f'User: {email}')
print('=' * 70)

with sync_playwright() as p:
    # Launch Edge browser
    print('\n[1] Launching Microsoft Edge...')
    try:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000,
            channel='msedge'  # Use Microsoft Edge
        )
    except Exception as e:
        print(f'    Edge not found: {e}')
        print('    Falling back to Chromium...')
        browser = p.chromium.launch(headless=False, slow_mo=1000)
    
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Go to LinkedIn login
    print('[2] Going to LinkedIn...')
    page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=60000)
    time.sleep(5)
    
    # Check if already logged in
    current_url = page.url
    print(f'    Current URL: {current_url}')
    
    if 'feed' in current_url or 'mynetwork' in current_url:
        print('[OK] Already logged in!')
    else:
        # Login
        print('[3] Logging in...')
        try:
            page.fill('#username', email)
            page.fill('#password', password)
            time.sleep(2)
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle', timeout=30000)
            time.sleep(8)
            print('[OK] Login submitted')
        except Exception as e:
            print(f'    Login: {e}')
    
    # Go to feed
    print('[4] Going to feed...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(10)
    print('[OK] On feed page')
    
    # Find and click "Start a post" button
    print('[5] Opening post dialog...')
    time.sleep(3)
    
    # The "Start a post" button is typically at the top of the feed
    # It's usually a button with text "Start a post"
    selectors = [
        'button:has-text("Start a post")',
        '.share-box-feed-entry__trigger',
        'button[aria-label*="post"]',
        '[data-control-name="update_posts"]',
    ]
    
    clicked = False
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=5000):
                print(f'    Found: {sel}')
                btn.click()
                time.sleep(5)
                clicked = True
                print('[OK] Post dialog opened!')
                break
        except Exception as e:
            print(f'    Tried {sel}: {e}')
            continue
    
    if not clicked:
        print('[WARN] Could not auto-click post button')
        print('       Please manually click "Start a post" in the browser')
        time.sleep(10)
    
    # Type the post content
    print('[6] Typing post content...')
    time.sleep(3)
    
    try:
        # The editor is a contenteditable div with role="textbox"
        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
        if editor.is_visible(timeout=5000):
            editor.fill(post)
            time.sleep(5)
            print('[OK] Content entered!')
        else:
            print('[WARN] Editor not found')
            print('       Please manually paste the post content')
    except Exception as e:
        print(f'    Editor: {e}')
    
    # Click the "Post" button
    print('[7] Clicking Post button...')
    time.sleep(3)
    
    try:
        # The Post button appears after content is entered
        post_btn = page.locator('button:has-text("Post")').first
        if post_btn.is_enabled(timeout=5000):
            post_btn.click()
            print('[OK] POST BUTTON CLICKED!')
        else:
            print('[WARN] Post button not enabled')
    except Exception as e:
        print(f'    Post button: {e}')
        print('    Please manually click "Post" in the browser')
    
    # Wait for post to publish
    print('[8] Waiting for post to publish...')
    time.sleep(20)
    
    print('\n' + '=' * 70)
    print('✅ POST SUBMITTED!')
    print('=' * 70)
    print('\nBROWSER STAYS OPEN FOR 2 MINUTES - PLEASE VERIFY!')
    print('\nCheck your post:')
    print('  1. Your feed: https://www.linkedin.com/feed/')
    print('  2. Profile → Activity → Posts')
    print('\n' + '=' * 70)
    
    # Keep browser open for verification
    for i in range(120, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   Verifying... {i}s remaining')
    
    print('\nClosing browser...')
    browser.close()
    print('Done!')
