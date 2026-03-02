
import argparse
import os
from datetime import datetime, timedelta
import re

ACCOUNTING_FILE = "AI_Employee_Vault/Accounting/Current_Month.md"
LOG_FILE_PATH = "vault/Logs/business.log"

# Ensure the accounting directory exists
if not os.path.exists(os.path.dirname(ACCOUNTING_FILE)):
    os.makedirs(os.path.dirname(ACCOUNTING_FILE))

# Ensure the log directory exists (as per previous MCP server creation)
if not os.path.exists(os.path.dirname(LOG_FILE_PATH)):
    os.makedirs(os.path.dirname(LOG_FILE_PATH))

# --- Helper Functions ---
def ensure_file_exists(filepath):
    """Ensures the accounting file exists with headers if it's new."""
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("| Date       | Type    | Amount  | Description              |
")
            f.write("|------------|---------|---------|--------------------------|
")

def parse_markdown_table(filepath):
    """Parses the Markdown table from the accounting file."""
    transactions = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Skip header and separator lines
            data_lines = lines[2:]
            for line in data_lines:
                parts = [p.strip() for p in line.strip().split('|')]
                if len(parts) == 5 and parts[0] == '' and parts[4] == '': # Ensure it's a valid row
                    try:
                        date_str, trans_type, amount_str, description = parts[1], parts[2], parts[3], parts[4]
                        amount = float(amount_str)
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        transactions.append({
                            'date': date_obj,
                            'type': trans_type,
                            'amount': amount,
                            'description': description
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse line '{line.strip()}': {e}")
    except FileNotFoundError:
        pass # File doesn't exist yet, will be created by ensure_file_exists
    return transactions

def format_transaction_row(date, trans_type, amount, description):
    """Formats a single transaction into a Markdown table row."""
    return f"| {date.strftime('%Y-%m-%d')} | {trans_type:<7} | {amount:>7.2f} | {description:<24} |
"

def log_activity(message):
    """Logs a message to the business log."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [ACCOUNTING_SCRIPT] {message}"
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_message + '
')
        print(f"Logged to {LOG_FILE_PATH}: {message}")
    except Exception as e:
        print(f"Error logging to {LOG_FILE_PATH}: {e}")

# --- Actions ---
def log_transaction(date_str, trans_type, amount, description):
    """Logs a new financial transaction."""
    ensure_file_exists(ACCOUNTING_FILE)
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if trans_type.lower() not in ['income', 'expense']:
            raise ValueError("Type must be 'income' or 'expense'.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        # Append new transaction to the file
        with open(ACCOUNTING_FILE, 'a', encoding='utf-8') as f:
            f.write(format_transaction_row(date_obj, trans_type.lower(), amount, description))
        
        log_activity(f"Logged transaction: {date_str}, {trans_type}, {amount:.2f}, {description}")
        print(f"Transaction logged successfully: {date_str}, {trans_type}, {amount:.2f}, {description}")

    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def generate_weekly_summary(end_date_str=None):
    """Generates a summary of transactions for the past 7 days."""
    ensure_file_exists(ACCOUNTING_FILE)
    transactions = parse_markdown_table(ACCOUNTING_FILE)

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid end_date format. Please use YYYY-MM-DD.")
            return
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=7)

    weekly_income = 0.0
    weekly_expense = 0.0
    
    summary_lines = [f"Weekly Financial Summary (ending {end_date.strftime('%Y-%m-%d')})"]
    summary_lines.append("========================================================")

    for t in transactions:
        if start_date <= t['date'] <= end_date:
            if t['type'] == 'income':
                weekly_income += t['amount']
            elif t['type'] == 'expense':
                weekly_expense += t['amount']
            
            # Format date for display
            display_date = t['date'].strftime('%Y-%m-%d')
            # Truncate description if too long for consistent display
            display_desc = (t['description'][:20] + '...') if len(t['description']) > 20 else t['description']
            summary_lines.append(f"- {display_date} | {t['type'].capitalize():<7} | {t['amount']:>8.2f} | {display_desc}")

    summary_lines.append("--------------------------------------------------------")
    summary_lines.append(f"Total Income: {weekly_income:>8.2f}")
    summary_lines.append(f"Total Expense: {weekly_expense:>8.2f}")
    summary_lines.append(f"Net: {weekly_income - weekly_expense:>10.2f}")
    summary_lines.append("========================================================")

    output = "
".join(summary_lines)
    print(output)
    log_activity(f"Generated weekly summary ending {end_date.strftime('%Y-%m-%d')}")

def generate_totals():
    """Generates total income and total expenses."""
    ensure_file_exists(ACCOUNTING_FILE)
    transactions = parse_markdown_table(ACCOUNTING_FILE)

    total_income = 0.0
    total_expense = 0.0

    for t in transactions:
        if t['type'] == 'income':
            total_income += t['amount']
        elif t['type'] == 'expense':
            total_expense += t['amount']

    output = f"Total Financial Summary:
========================================================
Total Income:  {total_income:>10.2f}
Total Expense: {total_expense:>10.2f}
Net:           {total_income - total_expense:>10.2f}
========================================================"
    print(output)
    log_activity("Generated total income/expense summary")

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Accounting Manager Skill")
    subparsers = parser.add_subparsers(dest="action", required=True, help="Available actions")

    # Log transaction sub-parser
    parser_log = subparsers.add_parser("log", help="Log a new financial transaction")
    parser_log.add_argument("--date", type=str, required=True, help="Date of the transaction (YYYY-MM-DD)")
    parser_log.add_argument("--type", type=str, required=True, choices=['income', 'expense'], help="Type of transaction (income/expense)")
    parser_log.add_argument("--amount", type=float, required=True, help="Amount of the transaction (must be positive)")
    parser_log.add_argument("--description", type=str, required=True, help="Description of the transaction")

    # Weekly summary sub-parser
    parser_weekly = subparsers.add_parser("weekly-summary", help="Generate a summary for the past 7 days")
    parser_weekly.add_argument("--end-date", type=str, help="Optional: End date for the summary (YYYY-MM-DD). Defaults to today.")

    # Totals sub-parser
    parser_totals = subparsers.add_parser("totals", help="Generate total income and expense")

    args = parser.parse_args()

    if args.action == "log":
        log_transaction(args.date, args.type, args.amount, args.description)
    elif args.action == "weekly-summary":
        generate_weekly_summary(args.end_date)
    elif args.action == "totals":
        generate_totals()

if __name__ == "__main__":
    main()
