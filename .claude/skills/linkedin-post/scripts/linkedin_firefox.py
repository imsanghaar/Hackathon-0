#!/usr/bin/env python3
"""
LinkedIn Post - Using Firefox with Persistent Context
This saves login session for reuse
"""

import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Credentials
email = 'imamsanghaar@gmail.com'
password = 'Sanghaar@2008'

# Persistent context path
user_data_dir = Path('/tmp/linkedin_user_data')
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

print('=' * 60)
print('LINKEDIN POST - PERSISTENT SESSION')
print('=' * 60)

with sync_playwright() as p:
    # Launch Firefox with persistent context
    print('\n[*] Launching Firefox with persistent context...')
    browser = p.firefox.launch(headless=False, slow_mo=1000)
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        storage_state_path=user_data_dir / 'storage.json' if (user_data_dir / 'storage.json').exists() else None
    )
    page = context.new_page()
    
    # Go to LinkedIn
    print('[*] Going to LinkedIn...')
    page.goto('https://www.linkedin.com/login', timeout=60000)
    time.sleep(5)
    
    # Check if already logged in
    if 'feed' in page.url:
        print('[OK] Already logged in!')
    else:
        print('[*] Logging in...')
        page.fill('#username', email)
        page.fill('#password', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(8)
        print('[OK] Logged in')
    
    # Go to feed
    print('[*] Going to feed...')
    page.goto('https://www.linkedin.com/feed/', timeout=60000)
    time.sleep(8)
    print('[OK] On feed')
    
    # Find and click "Start a post"
    print('[*] Finding post button...')
    time.sleep(3)
    
    # The post button is usually at the top of the feed
    # It says "Start a post"
    try:
        # Wait for the button to be visible
        post_btn = page.locator('button:has-text("Start a post")').first
        post_btn.wait_for(state='visible', timeout=10000)
        post_btn.click()
        print('[OK] Post dialog opened!')
        time.sleep(5)
    except Exception as e:
        print(f'[WARN] Post button: {e}')
        print('     Please manually click "Start a post" in the browser')
    
    # Type content
    print('[*] Typing post content...')
    time.sleep(3)
    
    try:
        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
        editor.wait_for(state='visible', timeout=10000)
        editor.fill(post)
        print('[OK] Content entered!')
        time.sleep(3)
    except Exception as e:
        print(f'[WARN] Editor: {e}')
    
    # Click Post button
    print('[*] Clicking Post button...')
    time.sleep(3)
    
    try:
        submit_btn = page.locator('button:has-text("Post")').first
        submit_btn.wait_for(state='enabled', timeout=10000)
        submit_btn.click()
        print('[OK] POST BUTTON CLICKED!')
    except Exception as e:
        print(f'[WARN] Submit: {e}')
        print('     Please manually click "Post" in the browser')
    
    # Wait for post to publish
    print('[*] Waiting for post to publish...')
    time.sleep(15)
    
    # Save storage state for next time
    try:
        context.storage_state(path=user_data_dir / 'storage.json')
        print('[OK] Session saved for next time')
    except:
        pass
    
    print('\n' + '=' * 60)
    print('POSTING COMPLETE!')
    print('=' * 60)
    print('\nBROWSER STAYS OPEN 90 SECONDS - VERIFY YOUR POST!')
    print('Check: https://www.linkedin.com/feed/')
    print('Or: Profile → Activity → Posts')
    print('=' * 60)
    
    # Keep browser open for verification
    for i in range(90, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   {i}s remaining...')
    
    browser.close()
    print('\nDone!')
