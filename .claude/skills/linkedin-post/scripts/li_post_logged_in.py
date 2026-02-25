#!/usr/bin/env python3
"""
LinkedIn Post - Already Logged In Version
User is already signed in, just posts the update
"""

import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

post_content = """🎉 Exciting Milestone Achieved! 🎉

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
print('LINKEDIN POST - ALREADY LOGGED IN')
print('=' * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Go to LinkedIn (user already logged in)
    print('\n[1] Going to LinkedIn feed...')
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
    time.sleep(8)
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_before_post.png')
    print('    ✓ On feed page - screenshot saved')
    
    # Find and click "Start a post" button
    print('\n[2] Finding "Start a post" button...')
    
    # Multiple selectors to try
    selectors = [
        ('button:has-text("Start a post")', 'Text button'),
        ('.share-box-feed-entry__trigger', 'Share box trigger'),
        ('button[aria-label*="post"]', 'Aria label button'),
        ('[data-control-name="update_posts"]', 'Control name button'),
        ('div[role="button"]:has-text("Start")', 'Role button'),
    ]
    
    clicked = False
    for selector, desc in selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=5000):
                print(f'    Found: {desc} ({selector})')
                btn.click()
                time.sleep(5)
                clicked = True
                print('    ✓ Clicked!')
                break
        except Exception as e:
            print(f'    Tried {desc}: {e}')
            continue
    
    if not clicked:
        print('\n    ⚠️  Could not find post button automatically')
        print('    Please manually click "Start a post" in the browser')
        print('    Waiting 30 seconds...')
        time.sleep(30)
    
    # Take screenshot of dialog
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_dialog_open.png')
    print('\n[3] Dialog screenshot saved')
    
    # Type the post content
    print('\n[4] Typing post content...')
    time.sleep(3)
    
    editor_selectors = [
        'div[role="textbox"][contenteditable="true"]',
        'div[aria-label*="What do you want"]',
        'div[placeholder*="post"]',
    ]
    
    typed = False
    for sel in editor_selectors:
        try:
            editor = page.locator(sel).first
            if editor.is_visible(timeout=5000):
                editor.fill(post_content)
                time.sleep(5)
                typed = True
                print(f'    ✓ Content entered using: {sel}')
                break
        except Exception as e:
            print(f'    Tried editor {sel}: {e}')
            continue
    
    if not typed:
        print('\n    ⚠️  Could not find editor')
        print('    Please manually paste the post content')
        time.sleep(20)
    
    # Take screenshot of content
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_content_entered.png')
    print('\n[5] Content screenshot saved')
    
    # Click Post button
    print('\n[6] Finding and clicking Post button...')
    time.sleep(3)
    
    post_btn_selectors = [
        ('button:has-text("Post")', 'Post text'),
        ('button:has-text("post")', 'post lowercase'),
        ('button[data-control-name*="post"]', 'Control name'),
    ]
    
    posted = False
    for selector, desc in post_btn_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_enabled(timeout=5000):
                print(f'    Found: {desc}')
                btn.click()
                posted = True
                print('    ✓ Post button clicked!')
                break
        except Exception as e:
            print(f'    Tried {desc}: {e}')
            continue
    
    if not posted:
        print('\n    ⚠️  Could not click Post button')
        print('    Please manually click "Post" in the browser')
    
    # Wait for post to publish
    print('\n[7] Waiting for post to publish...')
    time.sleep(15)
    
    # Final screenshot
    page.screenshot(path='/mnt/e/ai_employee/[Bronze_Tier](Silver_Tier)/li_after_post.png')
    print('    ✓ Final screenshot saved')
    
    print('\n' + '=' * 70)
    print('POSTING COMPLETE!')
    print('=' * 70)
    print('\nScreenshots saved:')
    print('  1. li_before_post.png - Before posting')
    print('  2. li_dialog_open.png - Dialog opened')
    print('  3. li_content_entered.png - Content entered')
    print('  4. li_after_post.png - After clicking Post')
    print('\nBROWSER STAYS OPEN FOR 2 MINUTES - PLEASE VERIFY THE POST')
    print('Check: https://www.linkedin.com/feed/ or your Profile → Activity')
    print('=' * 70)
    
    # Keep browser open for verification
    for i in range(120, 0, -1):
        time.sleep(1)
        if i % 30 == 0:
            print(f'   Verifying... {i}s remaining')
    
    print('\nClosing browser...')
    browser.close()
    print('Done!')
