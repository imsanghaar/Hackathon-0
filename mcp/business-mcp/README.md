# Business MCP Server

A production-ready **Model Context Protocol (MCP)** server for external business operations. This server provides standardized tools for sending emails, creating LinkedIn posts, and logging business activities.

## Features

| Capability | Tool Name | Description |
|------------|-----------|-------------|
| **Send Emails** | `send_email` | Send emails via SMTP with configurable settings |
| **Create LinkedIn Posts** | `post_linkedin` | Publish content to LinkedIn (requires API token) |
| **Log Business Actions** | `log_activity` | Record business activities to `vault/Logs/business.log` |

## Requirements

- **Python 3.10+** (required for MCP SDK)
- **pip** or **uv** package manager

## Installation

### Option 1: Using pip

```bash
# Navigate to the server directory
cd mcp/business-mcp/

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using uv (recommended for speed)

```bash
cd mcp/business-mcp/
uv venv
uv pip install -r requirements.txt
```

## Configuration

Set the following environment variables before running the server:

### Email Configuration (Required for send_email)

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | `587` |
| `EMAIL_USERNAME` | Email address for sending | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | Email password or app password | `your_app_password` |
| `EMAIL_FROM` | From address (defaults to EMAIL_USERNAME) | `noreply@company.com` |
| `EMAIL_USE_TLS` | Enable TLS encryption | `true` or `false` |

### LinkedIn Configuration (Optional for post_linkedin)

| Variable | Description | Example |
|----------|-------------|---------|
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn API access token | `AQV...` |
| `LINKEDIN_PERSON_URN` | LinkedIn person URN | `urn:li:person:ABC123` |

### General Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `PROJECT_ROOT` | Root directory for log file path | `E:\ai_employee\Hackathon-0` |

### Using a `.env` File

Create a `.env` file in the `mcp/business-mcp/` directory:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=noreply@company.com
EMAIL_USE_TLS=true

# LinkedIn Configuration (optional)
LINKEDIN_ACCESS_TOKEN=AQV...
LINKEDIN_PERSON_URN=urn:li:person:ABC123

# General
PROJECT_ROOT=E:\ai_employee\Hackathon-0
```

## Running the Server

### As an MCP Server (stdio transport)

```bash
cd mcp/business-mcp/
python server.py
```

The server will run using stdio transport, which is the standard MCP communication method.

### Integrating with MCP Clients

Add the server to your MCP client configuration. Example for Claude Desktop:

```json
{
  "mcpServers": {
    "business-mcp": {
      "command": "python",
      "args": ["E:/ai_employee/Hackathon-0/mcp/business-mcp/server.py"],
      "env": {
        "EMAIL_HOST": "smtp.gmail.com",
        "EMAIL_PORT": "587",
        "EMAIL_USERNAME": "your_email@gmail.com",
        "EMAIL_PASSWORD": "your_app_password",
        "EMAIL_USE_TLS": "true",
        "PROJECT_ROOT": "E:\\ai_employee\\Hackathon-0"
      }
    }
  }
}
```

## Available Tools

### 1. send_email

Send an email to a recipient.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body content

**Example Usage:**
```
Use send_email with:
  to: "client@example.com"
  subject: "Meeting Confirmation"
  body: "Dear Client, This is to confirm our meeting tomorrow at 10 AM."
```

**Response:**
```json
{"status": "success", "message": "Email sent to client@example.com"}
```

### 2. post_linkedin

Create a post on LinkedIn.

**Parameters:**
- `content` (string, required): The content to post on LinkedIn

**Example Usage:**
```
Use post_linkedin with:
  content: "Excited to announce our new product launch! #innovation #business"
```

**Response:**
```json
{"status": "success", "message": "LinkedIn post created: urn:li:share:123456789"}
```

**Note:** If `LINKEDIN_ACCESS_TOKEN` is not configured, the post request will be logged but not actually published.

### 3. log_activity

Log business activities to the business log file.

**Parameters:**
- `messages` (array of strings, required): List of messages to log

**Example Usage:**
```
Use log_activity with:
  messages: ["User logged in", "Payment processed for order #12345"]
```

**Response:**
```json
{"status": "success", "message": "2 messages logged"}
```

**Log Location:** `${PROJECT_ROOT}/vault/Logs/business.log`

## Logging

All business actions are logged to `${PROJECT_ROOT}/vault/Logs/business.log` with timestamps:

```
2026-03-02 10:30:45,123 - business-mcp - INFO - Email sent successfully to client@example.com with subject: Meeting Confirmation
2026-03-02 10:31:00,456 - business-mcp - INFO - BUSINESS_ACTIVITY: User logged in
2026-03-02 10:31:01,789 - business-mcp - INFO - BUSINESS_ACTIVITY: Payment processed for order #12345
```

## Production Deployment

### Security Best Practices

1. **Never hardcode credentials** - Always use environment variables or a secrets manager
2. **Use app-specific passwords** for email services with 2FA enabled
3. **Restrict network access** - The stdio transport is secure by default
4. **Validate inputs** - The server validates all required parameters

### Running with a Process Manager

For production, use a process manager like systemd (Linux) or NSSM (Windows):

**Example systemd service:**
```ini
[Unit]
Description=Business MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/business-mcp
Environment="EMAIL_HOST=smtp.gmail.com"
Environment="EMAIL_PORT=587"
Environment="EMAIL_USERNAME=your_email@gmail.com"
Environment="EMAIL_PASSWORD=your_app_password"
Environment="PROJECT_ROOT=/opt/business-mcp"
ExecStart=/opt/business-mcp/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV PROJECT_ROOT=/app

CMD ["python", "server.py"]
```

## Troubleshooting

### Email Sending Fails

1. Check SMTP credentials are correct
2. For Gmail, enable "Less secure app access" or use an App Password
3. Verify `EMAIL_PORT` matches your provider (587 for TLS, 465 for SSL)

### LinkedIn Posting Fails

1. Ensure `LINKEDIN_ACCESS_TOKEN` is valid and not expired
2. Check that your LinkedIn app has the necessary permissions
3. Verify `LINKEDIN_PERSON_URN` is correct

### Log File Not Created

1. Ensure `PROJECT_ROOT` environment variable is set correctly
2. Check that the `vault/Logs/` directory exists and is writable
3. Verify the server process has write permissions

## License

MIT License - See LICENSE file for details.

## Support

For issues or questions, please open an issue in the project repository.
