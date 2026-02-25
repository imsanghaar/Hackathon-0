#!/usr/bin/env python3
"""
Gmail Send - Production Ready

Send real emails using SMTP with Gmail.
Requires EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.

Usage:
    python send_email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
"""

import os
import sys
import argparse
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# Auto-load .env file from project root
def load_env():
    """Load environment variables from .env file"""
    script_dir = Path(__file__).parent.resolve()
    # Navigate up to find project root
    for _ in range(5):
        env_file = script_dir / '.env'
        if env_file.exists():
            break
        script_dir = script_dir.parent
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

# Load .env before anything else
load_env()


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def send_email(to_address: str, subject: str, body: str) -> dict:
    """
    Send email via Gmail SMTP.
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    # Get credentials from environment
    email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    if not email_address:
        return {'success': False, 'message': 'EMAIL_ADDRESS not set in environment'}
    
    if not email_password:
        return {'success': False, 'message': 'EMAIL_PASSWORD not set in environment'}
    
    # Validate recipient email
    if not validate_email(to_address):
        return {'success': False, 'message': f'Invalid email format: {to_address}'}
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, email_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        # Log the sent email
        log_email_sent(to_address, subject)
        
        return {'success': True, 'message': f'Email sent successfully to {to_address}'}
        
    except smtplib.SMTPAuthenticationError:
        return {'success': False, 'message': 'SMTP authentication failed. Check EMAIL_PASSWORD (use app password)'}
    except smtplib.SMTPConnectError:
        return {'success': False, 'message': 'Failed to connect to Gmail SMTP server'}
    except Exception as e:
        return {'success': False, 'message': f'Failed to send email: {str(e)}'}


def log_email_sent(to_address: str, subject: str) -> None:
    """Log sent email to file"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, '..', '..', '..', 'Logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'emails_sent.log')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] To: {to_address} | Subject: {subject}\n')
    except Exception:
        pass  # Don't fail if logging fails


def main():
    parser = argparse.ArgumentParser(description='Send email via Gmail SMTP')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body text')
    
    args = parser.parse_args()
    
    result = send_email(args.to, args.subject, args.body)
    
    if result['success']:
        print(f"SUCCESS: {result['message']}")
        sys.exit(0)
    else:
        print(f"ERROR: {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
