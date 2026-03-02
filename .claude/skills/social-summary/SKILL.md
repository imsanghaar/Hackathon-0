---
name: social-summary
description: Logs social media posts (LinkedIn, Twitter, etc.) to AI_Employee_Vault/Reports/Social_Log.md with platform, content, and date tracking.
---

# Social Media Summary Skill

## Overview

This skill provides centralized logging for all social media activity. After each post (LinkedIn, Twitter, etc.), it saves a summary to a unified log file for tracking and reporting purposes.

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Platform Support** | LinkedIn, Twitter, Facebook, and other platforms |
| **Automatic Logging** | Log posts immediately after publishing |
| **Summary Statistics** | Track total posts per platform |
| **Export to CSV** | Export logs for external analysis |
| **Markdown Format** | Human-readable log file |

## Installation

No additional dependencies required. Uses Python standard library.

## Usage

### Log a LinkedIn Post

```bash
python .claude/skills/social-summary/scripts/social_summary.py --log \
  --platform linkedin \
  --content "Excited to share our new product launch! #innovation"
```

**Output:**
```
[OK] Post logged to AI_Employee_Vault/Reports/Social_Log.md
     Platform: LinkedIn
     Date: 2026-03-02
     Preview: Excited to share our new product launch! #innovation
```

### Log with Specific Date

```bash
python .claude/skills/social-summary/scripts/social_summary.py --log \
  --platform linkedin \
  --content "Post content here" \
  --date 2026-03-01
```

### View Recent Posts

```bash
# View last 10 posts (default)
python .claude/skills/social-summary/scripts/social_summary.py --view

# View last 20 posts
python .claude/skills/social-summary/scripts/social_summary.py --view --limit 20
```

**Output:**
```
============================================================
         Recent Social Media Posts
============================================================

1. [2026-03-02] LinkedIn
   Content: Excited to share our new product launch! #innovation...

2. [2026-03-01] Twitter
   Content: Quick update on our latest features...

============================================================
```

### Show Statistics

```bash
python .claude/skills/social-summary/scripts/social_summary.py --stats
```

**Output:**
```
============================================================
         Social Media Statistics
============================================================
Total Posts: 15
LinkedIn: 10
Twitter: 3
Facebook: 1
Other: 1
Last Post: 2026-03-02
============================================================
```

### Export to CSV

```bash
# Export to default location
python .claude/skills/social-summary/scripts/social_summary.py --export

# Export to custom path
python .claude/skills/social-summary/scripts/social_summary.py --export \
  --output /path/to/export.csv
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--log` | Log a social media post | - |
| `--view` | View recent posts | - |
| `--export` | Export to CSV | - |
| `--stats` | Show statistics | - |
| `--platform` | Platform name | LinkedIn |
| `--content` | Post content | - |
| `--date` | Post date (YYYY-MM-DD) | Today |
| `--limit` | Number of posts to view | 10 |
| `--output` | CSV export path | Reports/Social_Log_Export.csv |

## Integration with LinkedIn Post Skills

### Automatic Integration

Add this to your LinkedIn post script:

```python
from pathlib import Path
import sys

# Add social-summary to path
sys.path.insert(0, str(Path(__file__).parent.parent / "social-summary" / "scripts"))
from social_summary import on_linkedin_post

def post_to_linkedin(content):
    """Post to LinkedIn and log automatically."""
    # Your LinkedIn posting logic
    result = linkedin_api.post(content)
    
    if result.success:
        # Log the post automatically
        on_linkedin_post(content)
    
    return result
```

### Manual Integration

After posting, call the log command:

```bash
# Post to LinkedIn
python .claude/skills/linkedin-post/scripts/post_linkedin.py --text "Content here"

# Then log it
python .claude/skills/social-summary/scripts/social_summary.py --log \
  --platform linkedin \
  --content "Content here"
```

## Log File Format

The social log is stored at `AI_Employee_Vault/Reports/Social_Log.md`:

```markdown
# Social Media Activity Log

This log tracks all social media posts across platforms.

## Summary Statistics

- **Total Posts:** 15
- **LinkedIn Posts:** 10
- **Twitter Posts:** 3
- **Facebook Posts:** 1
- **Other Posts:** 1
- **Last Post:** 2026-03-02

---

## Post History

| Date | Platform | Content Preview | Full Content |
|------|----------|-----------------|--------------|
| 2026-03-02 | LinkedIn | Excited to share our new... | Excited to share our new product launch! #innovation |
| 2026-03-01 | Twitter | Quick update on our... | Quick update on our latest features... |
```

## CSV Export Format

```csv
Date,Platform,Content
2026-03-02,LinkedIn,"Excited to share our new product launch! #innovation"
2026-03-01,Twitter,"Quick update on our latest features..."
```

## File Structure

```
social-summary/
├── scripts/
│   └── social_summary.py      # Main logging script
└── SKILL.md                   # This documentation

AI_Employee_Vault/Reports/
├── Social_Log.md              # Main log file
└── Social_Log_Export.csv      # Exported data (optional)
```

## Python API

### Log a Post

```python
from social_summary import save_post

success = save_post(
    platform="LinkedIn",
    content="Your post content here",
    date="2026-03-02"  # Optional, defaults to today
)
```

### LinkedIn Callback

```python
from social_summary import on_linkedin_post

# After posting to LinkedIn
on_linkedin_post("Post content here")
```

### Load Posts

```python
from social_summary import load_posts

posts = load_posts()
for post in posts:
    print(f"{post['date']} - {post['platform']}: {post['content']}")
```

### View Recent Posts

```python
from social_summary import view_posts

recent = view_posts(limit=5)
for post in recent:
    print(post['content'])
```

### Export to CSV

```python
from social_summary import export_to_csv

path = export_to_csv("/path/to/output.csv")
print(f"Exported to: {path}")
```

## Best Practices

1. **Log immediately** - Call log function right after posting
2. **Include full content** - Store complete post text for records
3. **Use consistent platform names** - LinkedIn, Twitter, Facebook (capitalized)
4. **Review monthly** - Check stats for posting frequency
5. **Export for reports** - Use CSV export for monthly reports

## Troubleshooting

### Posts Not Logging

1. Check content is provided: `--content "text"`
2. Verify Reports folder exists
3. Check file permissions

### Statistics Incorrect

1. View raw log file: `cat AI_Employee_Vault/Reports/Social_Log.md`
2. Re-run stats command
3. Check for malformed table rows

### Export Fails

1. Ensure posts exist in log
2. Check output path is writable
3. Verify CSV format compatibility

## Example Workflow

```bash
# 1. Create and post content
python .claude/skills/linkedin-post/scripts/post_linkedin.py \
  --text "Excited to announce our Q1 results!"

# 2. Log the post
python .claude/skills/social-summary/scripts/social_summary.py --log \
  --platform linkedin \
  --content "Excited to announce our Q1 results!"

# 3. View recent activity
python .claude/skills/social-summary/scripts/social_summary.py --view

# 4. Check statistics
python .claude/skills/social-summary/scripts/social_summary.py --stats

# 5. Export for monthly report
python .claude/skills/social-summary/scripts/social_summary.py --export \
  --output Reports/March_2026_Social_Report.csv
```

---

**Version:** 1.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System
