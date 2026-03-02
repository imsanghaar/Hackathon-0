# Accounting Manager Skill

## Description

This skill manages financial accounting data by maintaining a file for current month's transactions and providing functionalities to log new entries, generate weekly summaries, and calculate total income and expenses.

## When to Use This Skill

Use this skill when you need to:

*   Record income or expenses.
*   Track financial transactions for the current month.
*   Generate a summary of financial activity for the past week.
*   Calculate total income and expenses.

## File Maintenance

*   **File:** `AI_Employee_Vault/Accounting/Current_Month.md`
*   **Purpose:** Stores all logged financial transactions for the current month.
*   **Format:** Markdown table with columns: `Date`, `Type`, `Amount`, `Description`.

## Functionalities

### 1. Log Transaction

Adds a new transaction to the `AI_Employee_Vault/Accounting/Current_Month.md` file.

**Arguments:**

*   `date` (string): The date of the transaction (e.g., "YYYY-MM-DD").
*   `type` (string): The type of transaction, must be either "income" or "expense".
*   `amount` (float): The amount of the transaction. Must be positive.
*   `description` (string): A brief description of the transaction.

**Example Usage:**

```bash
/run scripts/accounting_manager.py --action log --date "2026-03-02" --type "expense" --amount 50.75 --description "Office supplies"
```

### 2. Generate Weekly Summary

Calculates and returns a summary of transactions for the past 7 days.

**Arguments:**

*   `end_date` (string, optional): The end date for the summary. Defaults to the current date. Format: "YYYY-MM-DD".

**Example Usage:**

```bash
/run scripts/accounting_manager.py --action weekly-summary
# or with a specific end date
/run scripts/accounting_manager.py --action weekly-summary --end-date "2026-03-01"
```

### 3. Generate Total Income/Expense

Calculates and returns the total income and total expenses logged in the `Current_Month.md` file.

**Example Usage:**

```bash
/run scripts/accounting_manager.py --action totals
```

## Bundled Resources

*   **`scripts/accounting_manager.py`**: The Python script that implements the functionalities described above. It handles file I/O, data parsing, and calculations.
