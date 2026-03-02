#!/usr/bin/env python3
"""
Human Approval - Production Ready

Human-in-the-loop approval for sensitive actions.
Creates approval request in Needs_Approval/ and waits for APPROVED or REJECTED.

Usage:
    python request_approval.py --action "Action description" --reason "Reason for approval"
    python request_approval.py --check "approval_file.txt"
    python request_approval.py --list
"""

import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path


# Get base directory - find project root by locating AI_Employee_Vault
SCRIPT_DIR = Path(__file__).parent.resolve()

# Navigate up to find the project root (where AI_Employee_Vault exists)
def find_project_root() -> Path:
    """Find project root by locating AI_Employee_Vault folder"""
    current = SCRIPT_DIR
    for _ in range(5):  # Go up max 5 levels
        if (current / 'AI_Employee_Vault').exists():
            return current
        current = current.parent
    return SCRIPT_DIR.parent.parent.parent  # Fallback

BASE_DIR = find_project_root()
VAULT_DIR = BASE_DIR / 'AI_Employee_Vault'
NEEDS_APPROVAL_DIR = VAULT_DIR / 'Needs_Approval'
LOGS_DIR = BASE_DIR / 'Logs'


def ensure_folders() -> None:
    """Ensure required folders exist"""
    NEEDS_APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def create_approval_request(action: str, reason: str, timeout_minutes: int = 60) -> dict:
    """
    Create an approval request file.
    
    Returns:
        dict: {'success': bool, 'file': str, 'message': str}
    """
    ensure_folders()
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"approval_{timestamp}.txt"
        filepath = NEEDS_APPROVAL_DIR / filename
        
        # Create approval request content
        content = f"""================================================================================
                        HUMAN APPROVAL REQUEST
================================================================================

Request ID: {timestamp}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Timeout: {timeout_minutes} minutes

--------------------------------------------------------------------------------
ACTION REQUESTED
--------------------------------------------------------------------------------
{action}

--------------------------------------------------------------------------------
REASON
--------------------------------------------------------------------------------
{reason}

--------------------------------------------------------------------------------
INSTRUCTIONS FOR HUMAN REVIEWER
--------------------------------------------------------------------------------
To APPROVE this action, change the status line below to:
STATUS: APPROVED

To REJECT this action, change the status line below to:
STATUS: REJECTED

Optionally add your name and comments in the Reviewer section.

--------------------------------------------------------------------------------
STATUS: PENDING
--------------------------------------------------------------------------------

Reviewer: _______________
Date: _______________
Comments: _______________

================================================================================
"""
        
        # Write the file
        with open(filepath, 'w') as f:
            f.write(content)
        
        # Log the request
        log_approval_request(filename, action)
        
        return {
            'success': True,
            'file': filename,
            'message': f'Approval request created: {filename}'
        }
        
    except Exception as e:
        return {'success': False, 'file': None, 'message': f'Failed to create request: {str(e)}'}


def check_approval_status(filename: str) -> dict:
    """
    Check the status of an approval request.

    Returns:
        dict: {'success': bool, 'status': str, 'message': str}
    """
    ensure_folders()

    try:
        filepath = NEEDS_APPROVAL_DIR / filename

        if not filepath.exists():
            return {'success': False, 'status': 'NOT_FOUND', 'message': f'File not found: {filename}'}

        # Read the file
        content = filepath.read_text()

        # Check for status - look for the status line between dashed separators
        # The actual status line appears after "Reviewer:" section header
        # Pattern: "--------------------------------------------------------------------------------\nSTATUS: XXX\n--------------------------------------------------------------------------------"
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for the dashed separator followed by STATUS line
            if line.strip().startswith('---') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('STATUS:'):
                    if 'APPROVED' in next_line:
                        return {'success': True, 'status': 'APPROVED', 'message': 'Action authorized by human reviewer'}
                    elif 'REJECTED' in next_line:
                        return {'success': True, 'status': 'REJECTED', 'message': 'Action denied by human reviewer'}
                    else:
                        return {'success': True, 'status': 'PENDING', 'message': 'Awaiting human review'}
        
        return {'success': True, 'status': 'PENDING', 'message': 'Awaiting human review'}
            
    except Exception as e:
        return {'success': False, 'status': 'ERROR', 'message': f'Failed to check status: {str(e)}'}


def wait_for_approval(filename: str, timeout_seconds: int = 3600, poll_interval: int = 10) -> dict:
    """
    Wait for approval decision.
    
    Returns:
        dict: {'success': bool, 'status': str, 'message': str}
    """
    start_time = time.time()
    
    print(f"Waiting for approval decision...")
    print(f"File: {filename}")
    print(f"Timeout: {timeout_seconds} seconds")
    print(f"Polling every {poll_interval} seconds")
    print("-" * 50)
    
    while time.time() - start_time < timeout_seconds:
        result = check_approval_status(filename)
        
        if not result['success']:
            return result
        
        if result['status'] == 'APPROVED':
            print(f"\n✓ APPROVED - Action authorized")
            log_approval_decision(filename, 'APPROVED')
            return result
        elif result['status'] == 'REJECTED':
            print(f"\n✗ REJECTED - Action denied")
            log_approval_decision(filename, 'REJECTED')
            return result
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Still pending...")
        time.sleep(poll_interval)
    
    # Timeout
    print(f"\n⏱ TIMEOUT - No response within {timeout_seconds} seconds")
    log_approval_decision(filename, 'TIMEOUT')
    return {'success': True, 'status': 'TIMEOUT', 'message': 'Timeout waiting for approval'}


def list_pending_approvals() -> dict:
    """List all pending approval requests"""
    ensure_folders()
    
    try:
        pending = []
        approved = []
        rejected = []
        
        for filepath in NEEDS_APPROVAL_DIR.iterdir():
            if not filepath.is_file():
                continue
            
            content = filepath.read_text()
            
            if 'STATUS: APPROVED' in content:
                approved.append(filepath.name)
            elif 'STATUS: REJECTED' in content:
                rejected.append(filepath.name)
            else:
                pending.append(filepath.name)
        
        return {
            'success': True,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'message': f'Pending: {len(pending)}, Approved: {len(approved)}, Rejected: {len(rejected)}'
        }
        
    except Exception as e:
        return {'success': False, 'pending': [], 'approved': [], 'rejected': [], 'message': str(e)}


def log_approval_request(filename: str, action: str) -> None:
    """Log approval request"""
    try:
        log_file = LOGS_DIR / 'approvals.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] REQUEST: {filename} - {action[:50]}...\n')
    except Exception:
        pass


def log_approval_decision(filename: str, status: str) -> None:
    """Log approval decision"""
    try:
        log_file = LOGS_DIR / 'approvals.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] {status}: {filename}\n')
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description='Human approval workflow')
    parser.add_argument('--action', help='Action requiring approval')
    parser.add_argument('--reason', default='No reason provided', help='Reason for approval request')
    parser.add_argument('--check', help='Check status of approval file')
    parser.add_argument('--wait', help='Wait for approval decision on file')
    parser.add_argument('--timeout', type=int, default=3600, help='Wait timeout in seconds (default: 3600)')
    parser.add_argument('--list', action='store_true', help='List all approval requests')
    
    args = parser.parse_args()
    
    if args.action:
        result = create_approval_request(args.action, args.reason)
        if result['success']:
            print(f"SUCCESS: {result['message']}")
            print(f"\nFile created: {result['file']}")
            print(f"Location: {NEEDS_APPROVAL_DIR}")
            print("\nHuman reviewer should:")
            print("  1. Open the file")
            print("  2. Review the action")
            print("  3. Change STATUS: PENDING to STATUS: APPROVED or STATUS: REJECTED")
            sys.exit(0)
        else:
            print(f"ERROR: {result['message']}")
            sys.exit(1)
    
    if args.check:
        result = check_approval_status(args.check)
        if result['success']:
            print(f"Status: {result['status']}")
            print(f"{result['message']}")
            sys.exit(0 if result['status'] != 'PENDING' else 1)
        else:
            print(f"ERROR: {result['message']}")
            sys.exit(1)
    
    if args.wait:
        result = wait_for_approval(args.wait, timeout_seconds=args.timeout)
        if result['success']:
            print(f"\nFinal Status: {result['status']}")
            sys.exit(0 if result['status'] == 'APPROVED' else 1)
        else:
            print(f"ERROR: {result['message']}")
            sys.exit(1)
    
    if args.list:
        result = list_pending_approvals()
        if result['success']:
            print(f"Approval Requests:")
            print(f"  Pending: {len(result['pending'])}")
            for f in result['pending'][:5]:
                print(f"    - {f}")
            print(f"  Approved: {len(result['approved'])}")
            for f in result['approved'][:5]:
                print(f"    - {f}")
            print(f"  Rejected: {len(result['rejected'])}")
            for f in result['rejected'][:5]:
                print(f"    - {f}")
            sys.exit(0)
        else:
            print(f"ERROR: {result['message']}")
            sys.exit(1)
    
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
