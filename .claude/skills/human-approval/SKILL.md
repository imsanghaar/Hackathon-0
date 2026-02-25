---
name: "human-approval"
description: "Human-in-the-loop approval for sensitive actions. Creates approval request and waits for APPROVED or REJECTED."
---

# Human Approval Skill

## When to Use
- Sensitive actions need human review
- Before executing critical operations
- Compliance requirements

## Usage
```bash
# Request approval
python .claude/skills/human-approval/scripts/request_approval.py --action "Delete database" --reason "Cleanup old records"

# Check status
python .claude/skills/human-approval/scripts/request_approval.py --check "approval_001.txt"
```

## Output Format
- PENDING: `Status: PENDING - Awaiting human review`
- APPROVED: `Status: APPROVED - Action authorized`
- REJECTED: `Status: REJECTED - Action denied`

## Important Rules
- Create file in Needs_Approval/
- Wait for APPROVED or REJECTED marker
- Log all approval requests
