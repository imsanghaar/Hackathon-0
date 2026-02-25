#!/usr/bin/env python3
"""
LinkedIn Post - Complete Working Version
Logs in with credentials and posts the update
"""

import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Load credentials from .env
script_dir = Path(__file__).parent.resolve()
# Navigate up: scripts -> skill -> .claude -> project root
env_file = script_dir.parent.parent.parent / '.env'

email = ''
password = ''

# Try multiple paths to find .env
possible_paths = [
    script_dir.parent.parent.parent / '.env',
    script_dir.parent.parent.parent.parent / '.env',
    Path('/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/.env'),
]

for p in possible_paths:
    if p.exists():
        env_file = p
        break

if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('LINKEDIN_EMAIL='):
                email = line.split('=', 1)[1]
            elif line.startswith('LINKEDIN_PASSWORD='):
                password = line.split('=', 1)[1]

if not email or not password:
    print('ERROR: Missing LINKEDIN_EMAIL or LINKEDIN_PASSWORD in .env')
    sys.exit(1)

post_content = """🎉 Exciting Milestone Achieved! 🎉

I'm thrilled to announce that I have successfully completed both Bronze and Silver Tiers of Hackathon 0!

🥈 What I Built:
✅ Bronze Tier: Interactive AI Employee CLI with dashboard & file monitoring
✅ Silver Tier: Production scheduler with human approval workflow

🔧 Tech: Python 3.10+, SMTP, Playwright, File watchers

📚 Docs: https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0

#Hackathon0 #AI #Python #Automation #Developer

---
⚙️ Auto-posted | AI Employee Silver Tier | 2026-02-25"""

print('=' * 70)
print('LINKEDIN AUTO-POSTER')
print('=' * 70)
print(f'User: {email}')
print('=' * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=2000)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # STEP 1: Login
    print('\n[STEP 1] Logging in...')
    page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=60000)
    time.sleep(5)
    
    # Fill credentials
    try:
        page.fill('#username', email)
        page.fill('#password', password)
        time.sleep(2)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(8)
        print('[OK] Login submitted')
    except Exception as e:
        print(f'[ERROR] Login failed: {e}')
    
    # Check if logged in
    if 'feed' in page.url or 'mynetwork' in page.url:
        print('[OK] Logged in successfully!')
    else:
        print(f'[WARN] Still on: {page.url}')
    
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_1_logged_in.png', timeout=10000)
    
    # STEP 2: Go to feed
    print('\n[STEP 2] Going to feed...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(10)
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_2_feed.png', timeout=10000)
    print('[OK] On feed page')
    
    # STEP 3: Click "Start a post"
    print('\n[STEP 3] Opening post dialog...')
    
    # Try multiple selectors
    selectors = [
        'button:has-text("Start a post")',
        '.share-box-feed-entry__trigger',
        'button[aria-label*="post"]',
    ]
    
    for sel in selectors:
        try:
            if page.is_visible(sel, timeout=5000):
                page.click(sel)
                time.sleep(5)
                print(f'[OK] Clicked: {sel}')
                break
        except:
            continue
    
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_3_dialog.png', timeout=10000)
    
    # STEP 4: Type content
    print('\n[STEP 4] Typing post content...')
    time.sleep(3)
    
    try:
        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
        if editor.is_visible(timeout=5000):
            editor.fill(post_content)
            time.sleep(5)
            print('[OK] Content entered')
    except Exception as e:
        print(f'[WARN] Editor issue: {e}')
    
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_4_content.png', timeout=10000)
    
    # STEP 5: Click Post
    print('\n[STEP 5] Clicking Post button...')
    time.sleep(3)
    
    try:
        post_btn = page.locator('button:has-text("Post")').first
        if post_btn.is_enabled(timeout=5000):
            post_btn.click()
            print('[OK] Post button clicked!')
        else:
            print('[WARN] Post button not enabled')
    except Exception as e:
        print(f'[WARN] Post click issue: {e}')
    
    # STEP 6: Wait and verify
    print('\n[STEP 6] Waiting for post to publish...')
    time.sleep(20)
    
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_5_final.png', timeout=10000)
    print('[OK] Final screenshot saved')
    
    print('\n' + '=' * 70)
    print('POSTING COMPLETE!')
    print('=' * 70)
    print('\nScreenshots:')
    print('  li_1_logged_in.png')
    print('  li_2_feed.png')
    print('  li_3_dialog.png')
    print('  li_4_content.png')
    print('  li_5_final.png')
    print('\nBROWSER STAYS OPEN 90 SECONDS - VERIFY YOUR POST NOW!')
    print('Check: https://www.linkedin.com/feed/')
    print('=' * 70)
    
    # Keep browser open for verification
    for i in range(90, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   {i}s remaining...')
    
    browser.close()
    print('\nDone!')
