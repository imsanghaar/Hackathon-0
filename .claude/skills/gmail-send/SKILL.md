---
name: "gmail-send"
description: "Send real emails via SMTP using Gmail. Requires EMAIL_ADDRESS and EMAIL_PASSWORD environment variables."
---

# Gmail Send Skill

## When to Use
- User asks to send an email
- User wants to notify someone
- Automated email notifications needed

## Usage
```bash
python .claude/skills/gmail-send/scripts/send_email.py --to "recipient@example.com" --subject "Subject" --body "Email body"
```

## Environment Variables Required
- `EMAIL_ADDRESS`: Your Gmail address
- `EMAIL_PASSWORD`: App password (not regular password)

## Output Format
- SUCCESS: `Email sent successfully to {recipient}`
- ERROR: `Failed: {error message}`

## Important Rules
- Use app password, not regular Gmail password
- Validate email format before sending
- Log all sent emails
