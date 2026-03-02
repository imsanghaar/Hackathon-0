# Agent Skills Setup Guide

## Quick Start

### 1. Environment Configuration

The `.env` file contains credentials for external services.

```bash
# Test your configuration
python load_env.py
```

### 2. Available Skills

| Skill | Status | Description |
|-------|--------|-------------|
| **gmail-send** | ✅ Ready | Send emails via Gmail SMTP |
| **linkedin-post** | ⏳ Waiting | Create LinkedIn posts (needs password) |
| **vault-file-manager** | ✅ Ready | Move files between vault folders |
| **human-approval** | ✅ Ready | Human-in-the-loop approvals |

---

## Configuration

### Gmail Setup

1. Go to Google Account Settings
2. Enable 2-Factor Authentication (if not enabled)
3. Visit: https://myaccount.google.com/apppasswords
4. Create an app password for "Mail"
5. Add to `.env`:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-16-char-app-password
   ```

### LinkedIn Setup

1. Use your regular LinkedIn email and password
2. Add to `.env`:
   ```
   LINKEDIN_EMAIL=your-email@email.com
   LINKEDIN_PASSWORD=your-password
   ```

**Note:** If you have 2FA enabled on LinkedIn, you may need to use an app-specific password or disable 2FA for automation.

---

## Usage Examples

### Send Email

```bash
python .claude/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "This is a test email"
```

### Create LinkedIn Post

```bash
python .claude/skills/linkedin-post/scripts/post_linkedin.py \
  --text "Excited to share my latest project!"
```

### Move Files

```bash
# Move to Done
python .claude/skills/vault-file-manager/scripts/move_task.py \
  --file "task.md" --to "Done"

# List all files
python .claude/skills/vault-file-manager/scripts/move_task.py --list
```

### Request Approval

```bash
# Create approval request
python .claude/skills/human-approval/scripts/request_approval.py \
  --action "Delete database records" \
  --reason "Cleanup old test data"

# Check status
python .claude/skills/human-approval/scripts/request_approval.py \
  --check "approval_*.txt"
```

---

## Security Notes

- ⚠️ **Never commit `.env` to Git** (already in `.gitignore`)
- 🔒 Use Gmail **app passwords**, not your regular password
- 🔒 Store credentials securely
- 📝 Review `.env.example` for template

---

## Troubleshooting

### Gmail Send Fails

1. Check if 2FA is enabled on your Google account
2. Generate a new app password
3. Verify EMAIL_ADDRESS is correct

### LinkedIn Post Fails

1. Verify credentials in `.env`
2. Check if LinkedIn requires CAPTCHA (may need manual login first)
3. Ensure Playwright is installed: `pip install playwright`

### File Operations Fail

1. Check folder permissions
2. Verify file exists: `ls AI_Employee_Vault/`
3. Use `--list` to see available files

---

## Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# For LinkedIn automation
pip install playwright
playwright install chromium
```

---

**Last Updated:** February 24, 2026
**Version:** 1.0
