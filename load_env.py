#!/usr/bin/env python3
"""
Load Environment Variables

Helper script to load .env file and verify required variables.
Run this to test your environment configuration.

Usage:
    python load_env.py
"""

import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
ENV_FILE = SCRIPT_DIR / '.env'


def load_env_file(filepath: Path) -> dict:
    """Load environment variables from .env file"""
    env_vars = {}
    
    if not filepath.exists():
        return env_vars
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def check_env():
    """Check environment configuration"""
    print("=" * 60)
    print("AI Employee - Environment Check")
    print("=" * 60)
    print()
    
    # Load .env file
    env_vars = load_env_file(ENV_FILE)
    
    if not env_vars:
        print(f"⚠️  WARNING: .env file not found at: {ENV_FILE}")
        print()
        print("Please create a .env file with your credentials.")
        print("See .env.example for template.")
        return False
    
    print(f"✓ .env file loaded: {ENV_FILE}")
    print()
    
    # Check Gmail configuration
    print("GMAIL SMTP:")
    email = env_vars.get('EMAIL_ADDRESS', '')
    password = env_vars.get('EMAIL_PASSWORD', '')
    
    if email:
        print(f"  ✓ EMAIL_ADDRESS: {email}")
    else:
        print(f"  ✗ EMAIL_ADDRESS: Not set")
    
    if password and password != 'your-gmail-app-password':
        # Mask password for display
        masked = password[:4] + '*' * (len(password) - 4) if len(password) > 4 else '****'
        print(f"  ✓ EMAIL_PASSWORD: {masked}")
    else:
        print(f"  ✗ EMAIL_PASSWORD: Not configured")
    
    print()
    
    # Check LinkedIn configuration
    print("LINKEDIN:")
    linkedin_email = env_vars.get('LINKEDIN_EMAIL', '')
    linkedin_password = env_vars.get('LINKEDIN_PASSWORD', '')
    
    if linkedin_email:
        print(f"  ✓ LINKEDIN_EMAIL: {linkedin_email}")
    else:
        print(f"  ✗ LINKEDIN_EMAIL: Not set")
    
    if linkedin_password and linkedin_password != 'your-linkedin-password':
        masked = linkedin_password[:4] + '*' * (len(linkedin_password) - 4) if len(linkedin_password) > 4 else '****'
        print(f"  ✓ LINKEDIN_PASSWORD: {masked}")
    else:
        print(f"  ⚠ LINKEDIN_PASSWORD: Not configured (will be added later)")
    
    print()
    print("=" * 60)
    
    # Summary
    gmail_ready = bool(email and password and password != 'your-gmail-app-password')
    linkedin_ready = bool(linkedin_email and linkedin_password and linkedin_password != 'your-linkedin-password')
    
    print("SKILL READINESS:")
    print(f"  gmail-send: {'✓ Ready' if gmail_ready else '✗ Needs configuration'}")
    print(f"  linkedin-post: {'✓ Ready' if linkedin_ready else '⚠ Waiting for password'}")
    print(f"  vault-file-manager: ✓ Ready (no env vars needed)")
    print(f"  human-approval: ✓ Ready (no env vars needed)")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    check_env()
