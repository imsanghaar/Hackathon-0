---
name: "gmail-watcher"
description: "Monitor Gmail for new emails with specific labels or from specific senders. Creates tasks in Inbox when matching emails are found. Uses Playwright MCP for browser automation."
---

# Gmail Watcher Skill

## When to Use

- User wants to monitor Gmail for new emails
- User wants to create tasks from important emails
- User needs to track emails from specific senders
- User wants to automate email-based task creation

## Procedure

1. **Start Playwright MCP Server** (if not running)
   ```bash
   # Start the MCP server
   npx @playwright/mcp@latest --port 8808 --shared-browser-context &
   ```

2. **Navigate to Gmail**
   - Use `browser_navigate` to go to gmail.com
   - Wait for page to load
   - Check if logged in

3. **Check for New Emails**
   - Look for unread emails
   - Check specific labels (if configured)
   - Check emails from specific senders (if configured)

4. **Create Tasks for Matching Emails**
   - For each matching email:
     - Extract subject, sender, date, preview
     - Create task file in `AI_Employee_Vault/Inbox/`
     - Mark email as processed (add label or star)

5. **Log Actions**
   - Log all checked emails
   - Log created tasks
   - Log any errors

## Output Format

**Task File Created in Inbox:**

```markdown
---
type: email_task
status: new
priority: medium
created_at: 2026-02-25 14:00:00
source: gmail
email_subject: "Project Update Required"
email_from: "client@example.com"
email_date: "2026-02-25 13:45:00"
---

# Email Task: Project Update Required

## Email Details

- **From:** client@example.com
- **Date:** 2026-02-25 13:45:00
- **Subject:** Project Update Required

## Email Preview

Hi, I need an update on the project status. Can you please send me...

## Required Actions

- [ ] Review email content
- [ ] Prepare project update
- [ ] Send response via email
- [ ] Update task status

---
*Created by Gmail Watcher*
```

**Action Log Entry:**
```log
[2026-02-25 14:00:00] GMAIL_WATCHER: Checked 15 emails
[2026-02-25 14:00:01] GMAIL_WATCHER: Found 2 unread emails
[2026-02-25 14:00:02] GMAIL_WATCHER: Created task for "Project Update Required"
[2026-02-25 14:00:02] GMAIL_WATCHER: Created task for "Meeting Request"
```

## Important Rules

- **Respect Privacy:** Only access emails user has permission to view
- **Don't Mark as Read:** Keep original email state unless configured
- **Rate Limiting:** Wait 2-3 seconds between actions
- **Error Handling:** Continue even if one email fails
- **Duplicate Prevention:** Don't create duplicate tasks for same email

## File Paths

- **Inbox:** `AI_Employee_Vault/Inbox/`
- **Log File:** `Logs/gmail_watcher.log`
- **Processed Tracker:** `Logs/gmail_processed.txt`
- **Script:** `.claude/skills/gmail-watcher/scripts/watch_gmail.py`

## Configuration

Create `.env` with:

```env
# Gmail Watcher Configuration
GMAIL_WATCH_LABELS=Important,Work
GMAIL_IGNORE_LABELS=Spam,Trash,Updates
GMAIL_CHECK_SENDERS=client@example.com,boss@company.com
GMAIL_CHECK_INTERVAL=300
```

## Running the Watcher

**Direct execution:**
```bash
python .claude/skills/gmail-watcher/scripts/watch_gmail.py
```

**With specific label:**
```bash
python .claude/skills/gmail-watcher/scripts/watch_gmail.py --label "Important"
```

**Dry run (no tasks created):**
```bash
python .claude/skills/gmail-watcher/scripts/watch_gmail.py --dry-run
```

**Continuous monitoring:**
```bash
python .claude/skills/gmail-watcher/scripts/watch_gmail.py --watch --interval 300
```

## Integration with Scheduler

Add to scheduler cycle:

```python
# In run_ai_employee.py or scheduler
from gmail_watcher import run_watcher
run_watcher()  # Check Gmail every cycle
```

## Example Workflow

1. **User says:** "Monitor my Gmail for important client emails"

2. **Gmail Watcher:**
   - Navigates to Gmail via Playwright MCP
   - Checks unread emails in "Important" label
   - Finds email from client@example.com
   - Creates task in Inbox/
   - Logs action

3. **Task Planner:**
   - Detects new task in Inbox
   - Creates execution plan
   - Moves to Needs_Action

4. **User:**
   - Reviews plan
   - Executes tasks
   - Marks complete

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't access Gmail | Ensure logged in, check 2FA settings |
| No emails found | Check label filters, verify inbox has unread emails |
| Duplicate tasks | Clear `Logs/gmail_processed.txt` |
| MCP server error | Restart: `npx @playwright/mcp@latest --port 8808` |

## Security Notes

- Never store Gmail credentials in code
- Use OAuth2 or app-specific passwords
- Don't log email content, only metadata
- Respect Gmail API rate limits
