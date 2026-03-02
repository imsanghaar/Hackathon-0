#!/usr/bin/env python3
"""
Business MCP Server - Production Ready

A Model Context Protocol (MCP) server for external business operations.
Provides capabilities for sending emails, creating LinkedIn posts, and logging business actions.

Server Name: business-mcp
"""

import os
import sys
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# =============================================================================
# Configuration
# =============================================================================

# Email Configuration (from environment variables)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USERNAME)

# Logging Configuration
PROJECT_ROOT = os.getenv("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "vault", "Logs", "business.log")

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("business-mcp")

# =============================================================================
# MCP Server Initialization
# =============================================================================

server = Server("business-mcp")

# =============================================================================
# Business Logic Functions
# =============================================================================


def send_email_action(to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Sends an email using configured SMTP settings.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    
    Returns:
        dict with status and message
    """
    if not EMAIL_USERNAME or EMAIL_USERNAME == "":
        raise ValueError("EMAIL_USERNAME environment variable is not configured")
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp_server:
            if EMAIL_USE_TLS:
                smtp_server.starttls()
            if EMAIL_PASSWORD:
                smtp_server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL_FROM, [to], msg.as_string())
        
        logger.info(f"Email sent successfully to {to} with subject: {subject}")
        return {"status": "success", "message": f"Email sent to {to}"}
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise ValueError(f"Email authentication failed: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        raise ValueError(f"Failed to send email: {e}")
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        raise ValueError(f"Failed to send email: {e}")


def post_linkedin_action(content: str) -> dict[str, Any]:
    """
    Posts content to LinkedIn.
    
    Args:
        content: The content to post on LinkedIn
    
    Returns:
        dict with status and message
    """
    try:
        # Check for LinkedIn API credentials
        linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        
        if not linkedin_token:
            logger.warning("LinkedIn access token not configured. Logging post request only.")
            logger.info(f"LINKEDIN_POST_REQUEST: {content[:200]}...")
            return {
                "status": "logged",
                "message": "LinkedIn post request logged (requires LINKEDIN_ACCESS_TOKEN for actual posting)"
            }
        
        # LinkedIn API integration (v2 API)
        import urllib.request
        import urllib.error
        import json
        
        api_url = "https://api.linkedin.com/v2/shares"
        headers = {
            "Authorization": f"Bearer {linkedin_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Get person URN from token if needed
        person_urn = os.getenv("LINKEDIN_PERSON_URN", "")
        
        payload = {
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": "PUBLIC"
        }
        
        if person_urn:
            payload["owner"] = person_urn
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            logger.info(f"LinkedIn post created successfully: {result.get('id', 'unknown')}")
            return {"status": "success", "message": f"LinkedIn post created: {result.get('id', 'unknown')}"}
    
    except Exception as e:
        logger.error(f"Failed to post to LinkedIn: {e}")
        raise ValueError(f"Failed to post to LinkedIn: {e}")


def log_activity_action(messages: list[str]) -> dict[str, Any]:
    """
    Logs business actions to the business log file.
    
    Args:
        messages: List of messages to log
    
    Returns:
        dict with status and message
    """
    try:
        logged_count = 0
        for message in messages:
            logger.info(f"BUSINESS_ACTIVITY: {message}")
            logged_count += 1
        
        return {"status": "success", "message": f"{logged_count} messages logged"}
    except Exception as e:
        logger.error(f"Failed to log business activity: {e}")
        raise ValueError(f"Failed to log business activity: {e}")

# =============================================================================
# MCP Tool Handlers
# =============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools provided by the Business MCP Server.
    """
    return [
        Tool(
            name="send_email",
            description="Send an email to a recipient with a subject and body content",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="post_linkedin",
            description="Create a post on LinkedIn with the provided content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to post on LinkedIn"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="log_activity",
            description="Log business actions and messages to the business activity log",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of messages to log"
                    }
                },
                "required": ["messages"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.
    
    Args:
        name: The name of the tool to call
        arguments: The arguments passed to the tool
    
    Returns:
        List of TextContent with the result
    """
    try:
        if name == "send_email":
            to = arguments.get("to", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "")
            
            if not to or not subject or not body:
                raise ValueError("Missing required arguments: to, subject, body")
            
            result = send_email_action(to, subject, body)
            return [TextContent(type="text", text=str(result))]
        
        elif name == "post_linkedin":
            content = arguments.get("content", "")
            
            if not content:
                raise ValueError("Missing required argument: content")
            
            result = post_linkedin_action(content)
            return [TextContent(type="text", text=str(result))]
        
        elif name == "log_activity":
            messages = arguments.get("messages", [])
            
            if not messages or not isinstance(messages, list):
                raise ValueError("Missing or invalid required argument: messages (must be a list)")
            
            result = log_activity_action(messages)
            return [TextContent(type="text", text=str(result))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool call failed for {name}: {e}")
        return [TextContent(type="text", text=f'{{"status": "error", "message": "{str(e)}"}}')]

# =============================================================================
# Server Entry Point
# =============================================================================


async def main():
    """
    Main entry point for the MCP server.
    Runs the server using stdio transport.
    """
    logger.info("Business MCP Server starting...")
    logger.info(f"Log file: {LOG_FILE_PATH}")
    logger.info(f"Email host: {EMAIL_HOST}:{EMAIL_PORT}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
