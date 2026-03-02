#!/usr/bin/env python3
"""
LinkedIn Post - Minimal Working Version
No screenshots, just login and post
"""

import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Load credentials
env_file = Path('/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/.env')
email = ''
password = ''

if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('LINKEDIN_EMAIL='):
                email = line.split('=', 1)[1]
            elif line.startswith('LINKEDIN_PASSWORD='):
                password = line.split('=', 1)[1]

if not email or not password:
    print('ERROR: Missing credentials in .env')
    sys.exit(1)

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
print('LINKEDIN AUTO-POSTER')
print('=' * 60)
print(f'User: {email}')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Login
    print('\n[1] Logging in...')
    page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=60000)
    time.sleep(3)
    page.fill('#username', email)
    page.fill('#password', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=30000)
    time.sleep(5)
    print('[OK] Logged in')
    
    # Go to feed
    print('[2] Going to feed...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(8)
    print('[OK] On feed')
    
    # Click post button
    print('[3] Opening post dialog...')
    try:
        page.click('button:has-text("Start a post")', timeout=10000)
        time.sleep(5)
        print('[OK] Dialog opened')
    except Exception as e:
        print(f'[WARN] {e}')
    
    # Type content
    print('[4] Typing content...')
    time.sleep(3)
    try:
        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
        editor.fill(post)
        time.sleep(5)
        print('[OK] Content entered')
    except Exception as e:
        print(f'[WARN] {e}')
    
    # Click Post
    print('[5] Clicking Post...')
    time.sleep(3)
    try:
        page.click('button:has-text("Post")', timeout=10000)
        print('[OK] Post clicked!')
    except Exception as e:
        print(f'[WARN] {e}')
    
    # Wait for publish
    print('[6] Waiting for post to publish...')
    time.sleep(20)
    
    print('\n' + '=' * 60)
    print('DONE! Post should be published.')
    print('=' * 60)
    print('\nBROWSER STAYS OPEN 60 SECONDS - VERIFY NOW!')
    print('Check: https://www.linkedin.com/feed/')
    print('=' * 60)
    
    # Keep browser open
    for i in range(60, 0, -1):
        time.sleep(1)
        if i % 15 == 0:
            print(f'   {i}s...')
    
    browser.close()
    print('\nDone!')
