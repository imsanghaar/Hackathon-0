---
name: "linkedin-post"
description: "Create LinkedIn posts using browser automation or manual posting. Supports Edge, Chrome, and Firefox."
---

# LinkedIn Post Skill

## When to Use
- Post updates to LinkedIn
- Share professional achievements
- Automated content posting

## Quick Start

### Option 1: Windows (Recommended - Uses Your Edge Browser)
```cmd
cd E:\ai_employee\[Bronze_Tier](Silver_Tier)
.claude\skills\linkedin-post\scripts\post_linkedin.bat
```
This opens LinkedIn in your Edge browser where you're already logged in.

### Option 2: Automated (WSL/Linux)
```bash
python .claude/skills/linkedin-post/scripts/linkedin_firefox.py
```

## Environment Variables
- `LINKEDIN_EMAIL`: Your LinkedIn email
- `LINKEDIN_PASSWORD`: Your LinkedIn password

## Manual Posting (Fallback)
If automation fails, manually post:
1. Go to linkedin.com
2. Click "Start a post"
3. Paste content
4. Click "Post"

## Output Format
- SUCCESS: Post published to LinkedIn
- ERROR: Describes what went wrong

## Important Rules
- Browser stays open for verification
- Session saved for reuse
- Supports multiple browsers
