#!/usr/bin/env python3
"""
LinkedIn Post - Interactive Mode
Keeps browser open for manual verification and help
"""

import os, sys, time
from pathlib import Path

# Load env
script_dir = Path(__file__).parent.resolve()
for _ in range(5):
    env_file = script_dir / '.env'
    if env_file.exists():
        break
    script_dir = script_dir.parent

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

post = """🎉 Exciting Milestone Achieved! 🎉

I'm thrilled to announce that I have successfully completed both Bronze and Silver Tiers of Hackathon 0!

🥈 What I Built:
✅ Bronze Tier: Interactive AI Employee CLI with real-time dashboard, file monitoring, and task management
✅ Silver Tier: Production-ready scheduler with human approval workflow, automated task planning, and continuous monitoring

🔧 Technologies Used:
• Python 3.10+
• SMTP (Gmail API)
• Playwright for browser automation
• File system watchers
• Human-in-the-loop approval system

📚 Documentation:
Hackathon 0 Docs: https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI/edit?tab=t.0

This project demonstrates practical AI automation with real-world applications including email notifications, social media posting, file management, and approval workflows.

#Hackathon0 #AI #Automation #Python #Developer #Achievement #ArtificialIntelligence #Coding

---
⚙️ Automated Post | AI Employee System (Silver Tier) | 2026-02-25"""

print('=' * 70)
print('LINKEDIN POST - INTERACTIVE MODE')
print('=' * 70)
print(f'Email: {email}')
print('=' * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Login
    print('\n[1] Going to LinkedIn login...')
    page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=60000)
    time.sleep(5)
    
    print('[2] Filling credentials...')
    page.fill('#username', email)
    page.fill('#password', password)
    time.sleep(2)
    
    print('[3] Clicking Sign In...')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=30000)
    time.sleep(8)
    
    print('[4] Going to feed...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(10)
    
    # Try to find post button with multiple strategies
    print('[5] Looking for "Start a post" button...')
    
    found = False
    selectors = [
        'button:has-text("Start a post")',
        '.share-box-feed-entry__trigger',
        'button[aria-label*="post"]',
    ]
    
    for sel in selectors:
        try:
            if page.is_visible(sel, timeout=5000):
                print(f'    Found: {sel}')
                page.click(sel)
                time.sleep(5)
                found = True
                break
        except:
            continue
    
    if not found:
        print('    ⚠️  Could not auto-find post button')
        print('    PLEASE MANUALLY CLICK "Start a post" IN THE BROWSER')
        print('    Waiting 30 seconds...')
        time.sleep(30)
    
    # Type content
    print('[6] Typing post content...')
    time.sleep(3)
    
    try:
        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
        if editor.is_visible(timeout=5000):
            editor.fill(post)
            time.sleep(5)
            print('    ✓ Content entered!')
        else:
            print('    ⚠️  Could not find editor - PLEASE MANUALLY PASTE:')
            print(post[:200] + '...')
            time.sleep(20)
    except Exception as e:
        print(f'    Error: {e}')
        print('    PLEASE MANUALLY ENTER THE POST CONTENT')
        time.sleep(30)
    
    # Click Post button
    print('[7] Looking for Post button...')
    time.sleep(3)
    
    try:
        post_btn = page.locator('button:has-text("Post")').first
        if post_btn.is_enabled(timeout=5000):
            post_btn.click()
            print('    ✓ Post button clicked!')
            time.sleep(15)
            
            # Screenshot
            page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_final_result.png')
            print('    ✓ Screenshot saved: li_final_result.png')
            
            print('\n' + '=' * 70)
            print('✅ POST SUBMITTED!')
            print('=' * 70)
            print('\nBROWSER STAYS OPEN FOR 2 MINUTES - PLEASE VERIFY:')
            print('  1. Check if post appears in your feed')
            print('  2. Go to Profile → Activity → Posts')
            print('\nScreenshot: li_final_result.png')
            print('=' * 70)
            
            # Keep browser open for 2 minutes for verification
            for i in range(120, 0, -1):
                time.sleep(1)
                if i % 30 == 0:
                    print(f'   Verifying... {i} seconds remaining')
            
            print('\nClosing browser...')
            browser.close()
            print('Done!')
        else:
            print('    ⚠️  Post button not enabled')
            print('    PLEASE MANUALLY CLICK POST IN THE BROWSER')
            print('    Waiting 60 seconds...')
            time.sleep(60)
            browser.close()
    except Exception as e:
        print(f'    Error: {e}')
        print('    PLEASE MANUALLY CLICK POST')
        print('    Waiting 60 seconds...')
        time.sleep(60)
        browser.close()
