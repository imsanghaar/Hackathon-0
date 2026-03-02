#!/usr/bin/env python3
"""
LinkedIn Post - Microsoft Edge Direct
Simple script to post on LinkedIn using Edge
"""

import time
from playwright.sync_api import sync_playwright

email = 'imamsanghaar@gmail.com'
password = 'Sanghaar@2008'

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
print('LINKEDIN POST - EDGE BROWSER')
print('=' * 70)

with sync_playwright() as p:
    # Launch Edge
    print('\nLaunching Edge...')
    browser = p.chromium.launch(
        channel='msedge',
        headless=False,
        args=['--start-maximized']
    )
    
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Go to LinkedIn
    print('Going to LinkedIn login...')
    page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=60000)
    time.sleep(5)
    
    # Login
    print('Filling credentials...')
    page.fill('#username', email)
    page.fill('#password', password)
    time.sleep(2)
    
    print('Clicking Sign In...')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=30000)
    time.sleep(8)
    
    # Go to feed
    print('Going to feed...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(10)
    
    print('\n' + '=' * 70)
    print('NOW FOLLOW THESE STEPS MANUALLY IF NEEDED:')
    print('=' * 70)
    print('1. Click "Start a post" button (top of feed)')
    print('2. Paste this content:')
    print('-' * 70)
    print(post)
    print('-' * 70)
    print('3. Click "Post" button')
    print('=' * 70)
    print('\nWaiting 3 minutes for you to complete...')
    print('Browser will stay open - check your post!')
    print('=' * 70)
    
    # Keep browser open
    for i in range(180, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   {i}s remaining...')
    
    browser.close()
    print('\nDone!')
