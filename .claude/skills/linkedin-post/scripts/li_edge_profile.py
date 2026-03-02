#!/usr/bin/env python3
"""
LinkedIn Post - Using Windows Edge Profile from WSL
Connects to existing Edge browser with user's logged-in session
"""

import time
from playwright.sync_api import sync_playwright

# Windows Edge user data directory
# This uses your existing Edge session where you're already logged in
edge_user_data = r'C:\Users\nemat\AppData\Local\Microsoft\Edge\User Data'

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
print('LINKEDIN POST - USING YOUR EDGE SESSION')
print('=' * 70)

with sync_playwright() as p:
    # Launch Edge with user's profile (from Windows)
    print('\nLaunching Edge with your profile...')
    browser = p.chromium.launch_persistent_context(
        user_data_dir=edge_user_data,
        channel='chrome',  # Try Chrome first
        headless=False,
        args=[
            '--start-maximized',
            '--disable-blink-features=AutomationControlled'
        ],
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # Go to LinkedIn
    print('Going to LinkedIn...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(8)
    
    print(f'Current URL: {page.url}')
    
    # Check if logged in
    if 'login' in page.url:
        print('Not logged in. Please login manually in the browser.')
        print('Waiting 60 seconds...')
        time.sleep(60)
    
    print('\n' + '=' * 70)
    print('BROWSER IS OPEN - PLEASE COMPLETE THE POST:')
    print('=' * 70)
    print('1. Click "Start a post" at top of feed')
    print('2. Copy and paste this content:')
    print('-' * 70)
    print(post)
    print('-' * 70)
    print('3. Click "Post"')
    print('=' * 70)
    print('\nWaiting 3 minutes for you to verify...')
    
    for i in range(180, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   {i}s remaining...')
    
    browser.close()
    print('\nDone!')
