---
type: maintenance
priority: high
created_at: 2026-03-02
---

# Database Cleanup Task

## Task Description

Delete old test records from the database that are older than 90 days.

## Required Actions

- Connect to production database
- Delete all records from test_tables where created_at < 90 days ago
- Verify deletion count
- Update cleanup log

## Warning

This is a permanent operation that cannot be undone.

## Authorization

Requires DBA approval before execution.
