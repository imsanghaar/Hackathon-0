#!/usr/bin/env python3
"""
Social Logger Module

Core logging functionality for social media activity.
Logs LinkedIn posts and other social media activity to Social_Log.md.

Usage:
    from social_logger import SocialLogger
    
    logger = SocialLogger()
    logger.log_post(
        platform="linkedin",
        content="Your post content",
        status="published"
    )
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
BASE_DIR = SKILL_DIR.parent.parent.parent  # Go up to project root

# File paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
REPOSTS_DIR = VAULT_DIR / "Reposts"
SOCIAL_LOG_FILE = REPOSTS_DIR / "Social_Log.md"

# Ensure directories exist
REPOSTS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SOCIAL LOGGER CLASS
# =============================================================================

class SocialLogger:
    """
    Social media activity logger.
    
    Logs posts to AI_Employee_Vault/Reposts/Social_Log.md
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
            self.reposts_dir = self.base_dir / "AI_Employee_Vault" / "Reposts"
        else:
            self.base_dir = BASE_DIR
            self.reposts_dir = REPOSTS_DIR
        
        self.log_file = self.reposts_dir / "Social_Log.md"
        self.reposts_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing posts
        self.posts = self._load_posts()
    
    def _load_posts(self) -> List[Dict[str, Any]]:
        """Load existing posts from JSON file."""
        json_file = self.reposts_dir / "social_posts.json"
        if not json_file.exists():
            return []

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("posts", [])
        except Exception as e:
            print(f"[WARN] Failed to load posts: {e}")
            return []
    
    def _save_posts(self) -> None:
        """Save posts to log file."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_posts": len(self.posts),
                "posts": self.posts
            }
            
            # Save as JSON for data management
            json_file = self.reposts_dir / "social_posts.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            # Generate markdown log
            self._generate_markdown_log()
            
        except Exception as e:
            print(f"[ERROR] Failed to save social log: {e}")
    
    def _generate_markdown_log(self) -> None:
        """Generate markdown Social_Log.md from posts data."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate stats
        platform_stats = {}
        this_week = 0
        this_month = 0
        now = datetime.now()
        
        for post in self.posts:
            platform = post.get("platform", "unknown")
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
            
            try:
                post_date = datetime.fromisoformat(post["timestamp"].replace("Z", "+00:00"))
                days_diff = (now - post_date.replace(tzinfo=None)).days
                if days_diff <= 7:
                    this_week += 1
                if days_diff <= 30:
                    this_month += 1
            except Exception:
                pass
        
        # Build markdown content
        md = f"""# Social Media Activity Log

**Generated:** {today}
**Total Posts:** {len(self.posts)}

---

## Recent Posts

| Date | Platform | Content | Status |
|------|----------|---------|--------|
"""
        
        # Add recent posts (last 10)
        for post in self.posts[-10:]:
            date = post.get("date", "Unknown")
            time = post.get("time", "")
            platform = post.get("platform", "unknown").title()
            content = post.get("content", "")[:50].replace("\n", " ")
            if len(post.get("content", "")) > 50:
                content += "..."
            status = post.get("status", "unknown")
            status_icon = {
                "published": "✅ Published",
                "scheduled": "⏰ Scheduled",
                "failed": "❌ Failed",
                "draft": "📝 Draft"
            }.get(status, status)
            
            md += f"| {date} {time} | {platform} | {content} | {status_icon} |\n"
        
        # Statistics section
        md += f"""
---

## Statistics

| Platform | Total Posts | This Week | This Month |
|----------|-------------|-----------|------------|
"""
        
        for platform, count in sorted(platform_stats.items(), key=lambda x: x[1], reverse=True):
            p_week = sum(1 for p in self.posts if p.get("platform") == platform and 
                        datetime.fromisoformat(p.get("timestamp", "").replace("Z", "+00:00")).replace(tzinfo=None) <= now and
                        (now - datetime.fromisoformat(p.get("timestamp", "").replace("Z", "+00:00")).replace(tzinfo=None)).days <= 7)
            p_month = sum(1 for p in self.posts if p.get("platform") == platform and
                        (now - datetime.fromisoformat(p.get("timestamp", "").replace("Z", "+00:00")).replace(tzinfo=None)).days <= 30)
            md += f"| {platform.title()} | {count} | {p_week} | {p_month} |\n"
        
        if not platform_stats:
            md += "| LinkedIn | 0 | 0 | 0 |\n"
        
        # Archive section
        md += f"""
---

## Archive

"""
        
        # Add all posts in reverse chronological order
        for post in reversed(self.posts):
            date = post.get("date", "Unknown")
            platform = post.get("platform", "unknown").title()
            content = post.get("content", "")
            posted = post.get("datetime", "Unknown")
            status = post.get("status", "unknown").title()
            
            md += f"""### {date} - {platform}

**Content:**
```
{content}
```

**Posted:** {posted}
**Status:** {status}

---

"""
        
        if not self.posts:
            md += "*No posts yet*\n\n"
        
        md += f"""*This log is automatically maintained by the Social Summary Skill.*
"""
        
        # Write markdown file
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(md)
    
    def log_post(
        self,
        platform: str,
        content: str,
        status: str = "published",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Log a social media post.
        
        Args:
            platform: Platform name (linkedin, twitter, facebook, etc.)
            content: Post content
            status: Post status (published, scheduled, failed, draft)
            extra_data: Additional data (hashtags, engagement, etc.)
            
        Returns:
            dict: Log result
        """
        timestamp = datetime.now()
        
        # Create post entry
        post = {
            "id": f"post_{timestamp.strftime('%Y%m%d%H%M%S')}",
            "platform": platform.lower(),
            "content": content,
            "status": status,
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "datetime": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": timestamp.isoformat(),
            "extra_data": extra_data or {}
        }
        
        # Add to posts list
        self.posts.append(post)
        
        # Save
        self._save_posts()
        
        return {
            "status": "logged",
            "id": post["id"],
            "platform": platform,
            "date": post["datetime"]
        }
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Get all logged posts."""
        return self.posts.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get social media statistics."""
        stats = {
            "total_posts": len(self.posts),
            "by_platform": {},
            "this_week": 0,
            "this_month": 0
        }
        
        now = datetime.now()
        
        for post in self.posts:
            platform = post.get("platform", "unknown")
            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
            
            try:
                post_date = datetime.fromisoformat(post["timestamp"].replace("Z", "+00:00"))
                days_diff = (now - post_date.replace(tzinfo=None)).days
                if days_diff <= 7:
                    stats["this_week"] += 1
                if days_diff <= 30:
                    stats["this_month"] += 1
            except Exception:
                pass
        
        return stats
    
    def export_to_json(self) -> str:
        """Export log to JSON format."""
        return json.dumps(self.posts, indent=2)
    
    def clear_log(self) -> bool:
        """Clear the log file."""
        try:
            self.posts = []
            self._save_posts()
            return True
        except Exception:
            return False


# =============================================================================
# MODULE FUNCTIONS
# =============================================================================

_default_logger: Optional[SocialLogger] = None


def get_logger() -> SocialLogger:
    """Get the default social logger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = SocialLogger()
    return _default_logger


def log_post(platform: str, content: str, status: str = "published") -> Dict[str, str]:
    """Log a social media post using the default logger."""
    return get_logger().log_post(platform, content, status)


def get_stats() -> Dict[str, Any]:
    """Get statistics using the default logger."""
    return get_logger().get_stats()
