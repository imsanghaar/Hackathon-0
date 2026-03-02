#!/usr/bin/env python3
"""
LinkedIn Post - Simple Auto-Login + Manual Post
Logs in and opens post dialog, then keeps browser open for verification
"""

import os, sys, time
from pathlib import Path

# Load env
script_dir = Path(__file__).parent.resolve()
env_file = script_dir.parent.parent.parent / '.env'

env_vars = {}
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

os.environ.setdefault('LINKEDIN_EMAIL', env_vars.get('LINKEDIN_EMAIL', ''))
os.environ.setdefault('LINKEDIN_PASSWORD', env_vars.get('LINKEDIN_PASSWORD', ''))

from playwright.sync_api import sync_playwright

email = os.environ['LINKEDIN_EMAIL']
password = os.environ['LINKEDIN_PASSWORD']

print('=' * 70)
print('LINKEDIN - AUTO LOGIN + MANUAL POST')
print('=' * 70)
print(f'User: {email}')
print('=' * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Login
    print('\n[*] Logging into LinkedIn...')
    page.goto('https://www.linkedin.com/login', timeout=60000)
    time.sleep(3)
    page.fill('#username', email)
    page.fill('#password', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=30000)
    time.sleep(5)
    print('[✓] Logged in!')
    
    # Go to feed
    print('[*] Going to feed...')
    page.goto('https://www.linkedin.com/feed/', timeout=60000)
    time.sleep(8)
    print('[✓] On feed page!')
    
    # Click post button
    print('[*] Opening post dialog...')
    try:
        page.click('button:has-text("Start a post")', timeout=10000)
        time.sleep(5)
        print('[✓] Post dialog opened!')
    except:
        print('[!] Could not open dialog - you may need to click manually')
    
    print('\n' + '=' * 70)
    print('BROWSER IS OPEN - PLEASE COMPLETE THE POST MANUALLY IF NEEDED')
    print('=' * 70)
    print('\nPost content to copy:')
    print('-' * 70)
    print("""🎉 Exciting Milestone Achieved! 🎉

I'm thrilled to announce that I have successfully completed both Bronze and Silver Tiers of Hackathon 0!

🥈 What I Built:
✅ Bronze Tier: Interactive AI Employee CLI with dashboard & file monitoring
✅ Silver Tier: Production scheduler with human approval workflow

🔧 Tech: Python, SMTP, Playwright, File watchers

📚 Docs: https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0

#Hackathon0 #AI #Python #Automation

---
⚙️ Auto-posted | AI Employee Silver Tier | 2026-02-25""")
    print('-' * 70)
    print('\nBrowser will stay open for 3 minutes for you to verify/complete')
    print('=' * 70)
    
    # Keep browser open
    for i in range(180, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   Browser open... {i}s remaining')
    
    browser.close()
    print('\nDone!')
