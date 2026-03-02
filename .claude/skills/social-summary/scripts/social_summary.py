#!/usr/bin/env python3
"""
Social Media Summary Skill

Logs social media posts (LinkedIn, etc.) to a centralized log file.

Function:
After LinkedIn Post:
- Save summary to: AI_Employee_Vault/Reports/Social_Log.md
- Include: Platform, Content, Date

Usage:
    python social_summary.py --platform linkedin --content "Post content here"
    python social_summary.py --log --platform linkedin --content "Post content" --date 2026-03-02
    python social_summary.py --view                   # View recent posts
    python social_summary.py --export                 # Export to CSV
"""

import os
import sys
import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
BASE_DIR = SCRIPT_DIR.parent.parent.parent.parent  # Go up to project root

# Folder paths
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
REPORTS_DIR = VAULT_DIR / "Reports"
SOCIAL_LOG_FILE = REPORTS_DIR / "Social_Log.md"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SOCIAL LOG MANAGEMENT
# =============================================================================

def ensure_social_log() -> None:
    """Ensure the social log file exists with proper headers."""
    if not SOCIAL_LOG_FILE.exists():
        # Create initial log file with header
        initial_content = """# Social Media Activity Log

This log tracks all social media posts across platforms.

## Summary Statistics

- **Total Posts:** 0
- **LinkedIn Posts:** 0
- **Twitter Posts:** 0
- **Facebook Posts:** 0
- **Other Posts:** 0
- **Last Post:** Never

---

## Post History

| Date | Platform | Content Preview | Full Content |
|------|----------|-----------------|--------------|
"""
        with open(SOCIAL_LOG_FILE, "w", encoding="utf-8") as f:
            f.write(initial_content)


def load_posts() -> List[Dict[str, str]]:
    """Load all posts from the social log."""
    posts = []
    
    if not SOCIAL_LOG_FILE.exists():
        return posts
    
    try:
        with open(SOCIAL_LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse table rows
        in_table = False
        for line in content.split("\n"):
            line = line.strip()
            
            if line.startswith("| Date |"):
                in_table = True
                continue
            
            if in_table and line.startswith("|"):
                parts = line.split("|")
                if len(parts) >= 5:
                    date = parts[1].strip()
                    platform = parts[2].strip()
                    preview = parts[3].strip()
                    full_content = parts[4].strip()
                    
                    if date and date != "------":
                        posts.append({
                            "date": date,
                            "platform": platform,
                            "preview": preview,
                            "content": full_content
                        })
    except Exception as e:
        print(f"[ERROR] Failed to load posts: {e}")
    
    return posts


def save_post(platform: str, content: str, date: Optional[str] = None) -> bool:
    """
    Save a new post to the social log.
    
    Args:
        platform: Social media platform (LinkedIn, Twitter, etc.)
        content: Full post content
        date: Post date (defaults to now)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_social_log()
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Create preview (first 50 chars)
        preview = content[:50] + "..." if len(content) > 50 else content
        
        # Escape pipe characters in content for markdown table
        escaped_content = content.replace("|", "\\|")
        escaped_preview = preview.replace("|", "\\|")
        
        # Read existing content
        with open(SOCIAL_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Find the table section and add new row
        new_lines = []
        table_found = False
        header_found = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            if "| Date | Platform |" in line:
                table_found = True
                header_found = True
            elif table_found and header_found and line.strip().startswith("|"):
                # Insert new row before this line
                new_row = f"| {date} | {platform} | {escaped_preview} | {escaped_content} |\n"
                new_lines.insert(len(new_lines) - 1, new_row)
                table_found = False
                header_found = False
                break
        
        # Update summary statistics
        posts = load_posts()
        posts.append({
            "date": date,
            "platform": platform,
            "preview": preview,
            "content": content
        })
        
        # Recalculate stats
        total_posts = len(posts)
        linkedin_posts = sum(1 for p in posts if p["platform"].lower() == "linkedin")
        twitter_posts = sum(1 for p in posts if p["platform"].lower() == "twitter")
        facebook_posts = sum(1 for p in posts if p["platform"].lower() == "facebook")
        other_posts = total_posts - linkedin_posts - twitter_posts - facebook_posts
        last_post = posts[-1]["date"] if posts else "Never"
        
        # Update stats section
        stats_content = f"""## Summary Statistics

- **Total Posts:** {total_posts}
- **LinkedIn Posts:** {linkedin_posts}
- **Twitter Posts:** {twitter_posts}
- **Facebook Posts:** {facebook_posts}
- **Other Posts:** {other_posts}
- **Last Post:** {last_post}

---

## Post History

"""
        
        # Find and replace stats section
        final_lines = []
        in_stats = False
        stats_replaced = False
        
        for line in new_lines:
            if "## Summary Statistics" in line:
                in_stats = True
                final_lines.append(stats_content)
                stats_replaced = True
            elif in_stats and line.strip().startswith("## Post History"):
                in_stats = False
                # Skip this line, already in stats_content
            elif in_stats:
                continue  # Skip old stats lines
            else:
                final_lines.append(line)
        
        # Write updated content
        with open(SOCIAL_LOG_FILE, "w", encoding="utf-8") as f:
            f.writelines(final_lines)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to save post: {e}")
        return False


def view_posts(limit: int = 10) -> List[Dict[str, str]]:
    """View recent posts."""
    posts = load_posts()
    return posts[-limit:] if posts else []


def export_to_csv(output_path: Optional[str] = None) -> Optional[str]:
    """Export posts to CSV format."""
    posts = load_posts()
    
    if not posts:
        return None
    
    if output_path is None:
        output_path = str(REPORTS_DIR / "Social_Log_Export.csv")
    
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Platform", "Content"])
            
            for post in posts:
                writer.writerow([post["date"], post["platform"], post["content"]])
        
        return output_path
        
    except Exception as e:
        print(f"[ERROR] Failed to export: {e}")
        return None


# =============================================================================
# LINKEDIN INTEGRATION
# =============================================================================

def on_linkedin_post(content: str, date: Optional[str] = None) -> bool:
    """
    Callback function triggered after a LinkedIn post.
    
    Args:
        content: The posted content
        date: Post date (defaults to now)
    
    Returns:
        True if logged successfully
    """
    return save_post("LinkedIn", content, date)


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_log(args):
    """Log a social media post."""
    platform = args.platform if args.platform else "LinkedIn"
    content = args.content if args.content else ""
    date = args.date if args.date else None
    
    if not content:
        print("[ERROR] Content is required. Use --content <text>")
        return 1
    
    success = save_post(platform, content, date)
    
    if success:
        print(f"[OK] Post logged to {SOCIAL_LOG_FILE}")
        print(f"     Platform: {platform}")
        print(f"     Date: {date or datetime.now().strftime('%Y-%m-%d')}")
        print(f"     Preview: {content[:50]}...")
        return 0
    else:
        print("[ERROR] Failed to log post")
        return 1


def cmd_view(args):
    """View recent posts."""
    limit = args.limit if args.limit else 10
    posts = view_posts(limit)
    
    print("=" * 60)
    print("         Recent Social Media Posts")
    print("=" * 60)
    
    if posts:
        for i, post in enumerate(reversed(posts), 1):
            print(f"\n{i}. [{post['date']}] {post['platform']}")
            print(f"   Content: {post['content'][:100]}...")
    else:
        print("\nNo posts logged yet.")
    
    print("\n" + "=" * 60)
    
    return 0


def cmd_export(args):
    """Export posts to CSV."""
    output_path = args.output if args.output else None
    result_path = export_to_csv(output_path)
    
    if result_path:
        print(f"[OK] Exported to {result_path}")
        return 0
    else:
        print("[ERROR] No posts to export or export failed")
        return 1


def cmd_stats(args):
    """Show statistics."""
    posts = load_posts()
    
    total = len(posts)
    linkedin = sum(1 for p in posts if p["platform"].lower() == "linkedin")
    twitter = sum(1 for p in posts if p["platform"].lower() == "twitter")
    facebook = sum(1 for p in posts if p["platform"].lower() == "facebook")
    other = total - linkedin - twitter - facebook
    
    print("=" * 60)
    print("         Social Media Statistics")
    print("=" * 60)
    print(f"Total Posts: {total}")
    print(f"LinkedIn: {linkedin}")
    print(f"Twitter: {twitter}")
    print(f"Facebook: {facebook}")
    print(f"Other: {other}")
    
    if posts:
        print(f"Last Post: {posts[-1]['date']}")
    
    print("=" * 60)
    
    return 0


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Social Media Summary Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log a LinkedIn post
  python social_summary.py --log --platform linkedin --content "Excited to share..."
  
  # Log with specific date
  python social_summary.py --log --platform linkedin --content "Post content" --date 2026-03-02
  
  # View recent posts
  python social_summary.py --view
  
  # View last 20 posts
  python social_summary.py --view --limit 20
  
  # Export to CSV
  python social_summary.py --export
  
  # Show statistics
  python social_summary.py --stats
        """
    )
    
    # Commands
    parser.add_argument("--log", action="store_true", help="Log a social media post")
    parser.add_argument("--view", action="store_true", help="View recent posts")
    parser.add_argument("--export", action="store_true", help="Export to CSV")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    # Options
    parser.add_argument("--platform", type=str, help="Platform name (LinkedIn, Twitter, etc.)")
    parser.add_argument("--content", type=str, help="Post content")
    parser.add_argument("--date", type=str, help="Post date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=10, help="Number of posts to view")
    parser.add_argument("--output", type=str, help="Output path for CSV export")
    
    args = parser.parse_args()
    
    if args.log:
        return cmd_log(args)
    elif args.view:
        return cmd_view(args)
    elif args.export:
        return cmd_export(args)
    elif args.stats:
        return cmd_stats(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
