#!/usr/bin/env python3
"""
Vault File Manager - Production Ready

Manage task workflow by moving files between vault folders.
Folders: Inbox/, Needs_Action/, Done/

Usage:
    python move_task.py --file "filename.md" --to "Done"
    python move_task.py --file "filename.md" --to "Needs_Action"
    python move_task.py --file "filename.md" --to "Inbox"
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path


# Get base directory - find project root by locating AI_Employee_Vault
SCRIPT_DIR = Path(__file__).parent.resolve()

def find_project_root() -> Path:
    """Find project root by locating AI_Employee_Vault folder"""
    current = SCRIPT_DIR
    for _ in range(5):
        if (current / 'AI_Employee_Vault').exists():
            return current
        current = current.parent
    return SCRIPT_DIR.parent.parent.parent

BASE_DIR = find_project_root()
VAULT_DIR = BASE_DIR / 'AI_Employee_Vault'

# Folder paths
INBOX_DIR = VAULT_DIR / 'Inbox'
NEEDS_ACTION_DIR = VAULT_DIR / 'Needs_Action'
DONE_DIR = VAULT_DIR / 'Done'

# Valid folders
VALID_FOLDERS = {'inbox': INBOX_DIR, 'needs_action': NEEDS_ACTION_DIR, 'done': DONE_DIR}


def ensure_folders() -> None:
    """Ensure all vault folders exist"""
    for folder in [INBOX_DIR, NEEDS_ACTION_DIR, DONE_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def find_file(filename: str) -> Path:
    """
    Find a file in any of the vault folders.
    
    Returns:
        Path to file or None if not found
    """
    for folder in [INBOX_DIR, NEEDS_ACTION_DIR, DONE_DIR]:
        if not folder.exists():
            continue
        file_path = folder / filename
        if file_path.exists() and file_path.is_file():
            return file_path
    return None


def move_file(filename: str, to_folder: str) -> dict:
    """
    Move a file to specified folder.
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    ensure_folders()
    
    # Normalize folder name
    to_folder_lower = to_folder.lower().replace(' ', '_').replace('-', '_')
    
    if to_folder_lower not in VALID_FOLDERS:
        return {'success': False, 'message': f'Invalid folder: {to_folder}. Use: Inbox, Needs_Action, or Done'}
    
    dest_folder = VALID_FOLDERS[to_folder_lower]
    
    # Find the file
    source_path = find_file(filename)
    
    if source_path is None:
        return {'success': False, 'message': f'File not found: {filename}'}
    
    # Check if already in destination
    if source_path.parent == dest_folder:
        return {'success': False, 'message': f'File already in {to_folder}'}
    
    # Create destination path
    dest_path = dest_folder / filename
    
    try:
        # Move the file
        shutil.move(str(source_path), str(dest_path))
        
        # Log the movement
        log_file_movement(filename, str(source_path.parent.name), to_folder)
        
        return {'success': True, 'message': f'Moved {filename} to {to_folder}'}
        
    except PermissionError:
        return {'success': False, 'message': f'Permission denied moving {filename}'}
    except Exception as e:
        return {'success': False, 'message': f'Failed to move file: {str(e)}'}


def log_file_movement(filename: str, from_folder: str, to_folder: str) -> None:
    """Log file movement"""
    try:
        logs_dir = BASE_DIR / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / 'file_movements.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] {filename}: {from_folder} -> {to_folder}\n')
    except Exception:
        pass


def list_files(folder: str = None) -> dict:
    """
    List files in vault folders.
    
    Returns:
        dict: {'success': bool, 'files': list, 'message': str}
    """
    ensure_folders()
    
    try:
        result = {}
        
        if folder:
            folder_lower = folder.lower().replace(' ', '_')
            if folder_lower not in VALID_FOLDERS:
                return {'success': False, 'files': [], 'message': f'Invalid folder: {folder}'}
            
            target = VALID_FOLDERS[folder_lower]
            if target.exists():
                files = [f.name for f in target.iterdir() if f.is_file()]
                result = {'success': True, 'files': files, 'message': f'{len(files)} files in {folder}'}
            else:
                result = {'success': True, 'files': [], 'message': f'{folder} is empty'}
        else:
            # List all folders
            for name, path in VALID_FOLDERS.items():
                if path.exists():
                    files = [f.name for f in path.iterdir() if f.is_file()]
                    result[name] = files
            result = {'success': True, 'files': result, 'message': 'Listed all folders'}
        
        return result
        
    except Exception as e:
        return {'success': False, 'files': [], 'message': f'Failed to list files: {str(e)}'}


def main():
    parser = argparse.ArgumentParser(description='Manage vault files')
    parser.add_argument('--file', help='Filename to move')
    parser.add_argument('--to', help='Destination folder (Inbox, Needs_Action, Done)')
    parser.add_argument('--list', action='store_true', help='List files in folders')
    parser.add_argument('--folder', help='Specific folder to list')
    
    args = parser.parse_args()
    
    if args.list:
        result = list_files(args.folder)
        if result['success']:
            if isinstance(result['files'], dict):
                print(f"Vault Contents:")
                for folder, files in result['files'].items():
                    print(f"  {folder}: {len(files)} files")
                    for f in files[:5]:
                        print(f"    - {f}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more")
            else:
                print(f"SUCCESS: {result['message']}")
                for f in result['files']:
                    print(f"  - {f}")
            sys.exit(0)
        else:
            print(f"ERROR: {result['message']}")
            sys.exit(1)
    
    if args.file and args.to:
        result = move_file(args.file, args.to)
        if result['success']:
            print(f"SUCCESS: {result['message']}")
            sys.exit(0)
        else:
            print(f"ERROR: {result['message']}")
            sys.exit(1)
    
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
