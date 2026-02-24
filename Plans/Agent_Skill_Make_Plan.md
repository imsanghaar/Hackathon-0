# Agent Skill: Make a Plan for Tasks

## Trigger Phrase
When the user says: **"Make a Plan for tasks"**

## Workflow

1. **Read all files in Needs_Action folder**
   - List all `.md` files in the Needs_Action directory
   - Read each task file's content and frontmatter

2. **Analyze pending tasks**
   - Identify task types from frontmatter (`type` field)
   - Note priorities (`priority` field)
   - Extract related files and sources
   - Identify any unclear or ambiguous items

3. **Create a new Plan file**
   - Location: `Plans/`
   - Filename format: `Plan_<timestamp>.md` (e.g., `Plan_2026-02-24_15-30-00.md`)

## Plan File Structure

```markdown
# Plan: <Date/Time>

## Summary of Pending Tasks
(List each task with brief description)

## Suggested Order of Execution
(Prioritized list with reasoning)

## Risks or Unclear Items
(Flag any ambiguous tasks or potential issues)

## Strategy
(Short paragraph describing the overall approach)
```

## Rules
- This is a **planning document only** - do not execute tasks
- Be concise but thorough in analysis
- Highlight any tasks that need clarification
- Consider task dependencies when suggesting order
