# 📱 Social Summary Skill - Quick Start Guide

## Overview

The **Social Summary Skill** automatically logs and summarizes social media activity, specifically LinkedIn posts.

| Feature | Description |
|---------|-------------|
| 📝 **Auto-Logging** | Logs posts after publishing |
| 📊 **Statistics** | Track posts by platform |
| 📅 **Date Tracking** | Timestamp for each post |
| 📋 **Content Archive** | Full post content preserved |
| 📤 **Export** | Export to JSON format |

---

## 🚀 Quick Start

### Log a LinkedIn Post

```bash
# Log a post
python .claude/skills/social-summary/scripts/social_summary.py --log --platform linkedin --content "Your post content here"

# Short version
python .claude/skills/social-summary/scripts/social_summary.py --log -p linkedin -c "Post content"
```

### View Social Log

```bash
# View recent posts
python .claude/skills/social-summary/scripts/social_summary.py --view

# View statistics
python .claude/skills/social-summary/scripts/social_summary.py --stats

# Export to JSON
python .claude/skills/social-summary/scripts/social_summary.py --export
```

---

## 📁 File Structure

```
social-summary/
├── scripts/
│   ├── social_summary.py      # CLI interface
│   └── social_logger.py       # Core logging module
├── SKILL.md                    # Full documentation
└── README.md                   # This quick start guide

AI_Employee_Vault/Reposts/
└── Social_Log.md               # Social media activity log
```

---

## 📋 Social_Log.md Format

```markdown
# Social Media Activity Log

**Generated:** 2026-03-02
**Total Posts:** 15

---

## Recent Posts

| Date | Platform | Content | Status |
|------|----------|---------|--------|
| 2026-03-02 10:00 | LinkedIn | Excited to announce... | ✅ Published |

---

## Statistics

| Platform | Total Posts | This Week | This Month |
|----------|-------------|-----------|------------|
| LinkedIn | 15 | 3 | 10 |

---

## Archive

### 2026-03-02 - LinkedIn

**Content:**
```
Excited to announce our new product launch!
#innovation #technology
```

**Posted:** 2026-03-02 10:00:00
**Status:** Published
```

---

## 🔧 CLI Commands

| Command | Description |
|---------|-------------|
| `--log` | Log a new post |
| `--platform` | Platform (linkedin, twitter, etc.) |
| `--content` | Post content |
| `--view` | View social log |
| `--stats` | Show statistics |
| `--export` | Export to JSON |
| `--clear` | Clear log |

---

## 📊 Sample Output

### Stats Command

```
============================================================
         Social Media Summary
============================================================

📊 Statistics:
  Total Posts: 15
  This Week: 3
  This Month: 10

Platform Breakdown:
  LinkedIn: 15 posts

============================================================
```

### Log Command

```
============================================================
         Logging Social Media Post
============================================================

[OK] Post logged successfully!
  Platform: linkedin
  Date: 2026-03-02 10:00:00
  ID: post_20260302100000

Log file: AI_Employee_Vault/Reposts/Social_Log.md
============================================================
```

---

## 🔗 Integration with LinkedIn Auto-Post

Add to your linkedin-auto-post skill:

```python
from social_logger import SocialLogger

# Initialize logger
social_logger = SocialLogger()

def post_to_linkedin(content):
    # Post to LinkedIn
    result = linkedin_api.post(content)
    
    # Log the post
    if result.success:
        social_logger.log_post(
            platform="linkedin",
            content=content,
            status="published"
        )
    else:
        social_logger.log_post(
            platform="linkedin",
            content=content,
            status="failed"
        )
```

---

## ⚙️ Configuration

Edit `social_logger.py` to customize:

```python
# File paths
SOCIAL_LOG_FILE = "AI_Employee_Vault/Reposts/Social_Log.md"

# Default platform
DEFAULT_PLATFORM = "linkedin"

# Supported platforms
SUPPORTED_PLATFORMS = ["linkedin", "twitter", "facebook", "instagram"]
```

---

## 🛠️ Troubleshooting

### Log Not Created

1. Check folder exists: `ls AI_Employee_Vault/Reposts/`
2. Verify write permissions
3. Run with --log to create initial log

### Statistics Not Updating

1. Check log file format
2. Verify posts are being logged
3. Run --view to check entries

---

## 📝 Best Practices

1. **Log immediately** - Log right after posting
2. **Include full content** - Preserve complete post text
3. **Track hashtags** - Add to extra_data
4. **Review weekly** - Check posting frequency
5. **Export monthly** - Archive old posts

---

## 🔗 Related Skills

| Skill | Integration |
|-------|-------------|
| **linkedin-auto-post** | Auto-logs after posting |
| **ceo-briefing** | Includes social stats in reports |
| **analytics-dashboard** | Displays social metrics |

---

## 📞 Support

For detailed documentation, see [SKILL.md](./SKILL.md)

**Version:** 1.0  
**Last Updated:** March 2, 2026  
**Author:** AI Employee System by ISC
