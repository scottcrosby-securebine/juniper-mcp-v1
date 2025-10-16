# Junos MCP Server - Deployment Guide

This guide provides comprehensive instructions for deploying the Junos MCP Server in various environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Methods](#deployment-methods)
  - [Option A: Docker Deployment](#option-a-docker-deployment)
  - [Option B: Local Python Deployment](#option-b-local-python-deployment)
- [Configuration](#configuration)
  - [Device Configuration](#device-configuration)
  - [Environment Variables](#environment-variables)
- [MCP Client Setup](#mcp-client-setup)
  - [Claude Desktop](#claude-desktop)
  - [VS Code](#vs-code)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Junos MCP Server enables AI assistants like Claude to interact with Juniper network devices through the Model Context Protocol (MCP). It supports two transport methods:

- **stdio**: For local desktop applications (Claude Desktop)
- **streamable-http**: For remote clients (VS Code, web applications)

## Prerequisites

### Required

- **Python 3.10 or higher** (for local deployment) or **Docker** (for containerized deployment)
- **Git** (to clone the repository)
- **Network access** to your Juniper devices
- **SSH credentials** (password or SSH key) for your devices

### Optional

- **Docker Desktop** (for Docker deployment)
- **Claude Desktop** or **VS Code** (MCP clients)

## Deployment Methods

### Option A: Docker Deployment

Docker provides an isolated, reproducible environment for running the server.

#### 1. Clone the Repository

```bash
git clone https://github.com/scottcrosby-securebine/juniper-mcp-v1.git
cd juniper-mcp-v1
```

#### 2. Prepare Device Configuration

Copy the template and configure your devices:

```bash
cp devices-template.json devices.json
# Edit devices.json with your actual device information
```

#### 3. Build the Docker Image

```bash
docker build -t juniper-mcp-v1:latest .
```

#### 4. Run the Container

**For stdio transport (Claude Desktop):**

```bash
docker run --rm -it \
  -v $(pwd)/devices.json:/app/config/devices.json \
  -v ~/.ssh/id_rsa:/app/keys/id_rsa:ro \
  juniper-mcp-v1:latest
```

**For streamable-http transport (VS Code, remote clients):**

```bash
docker run --rm -it \
  -v $(pwd)/devices.json:/app/config/devices.json \
  -v ~/.ssh/id_rsa:/app/keys/id_rsa:ro \
  -p 30030:30030 \
  juniper-mcp-v1:latest \
  python jmcp.py -f /app/config/devices.json -t streamable-http -H 0.0.0.0 -p 30030
```

**Notes:**
- Replace `~/.ssh/id_rsa` with your actual SSH private key path
- The `:ro` flag mounts the key as read-only for security
- For streamable-http, the port 30030 is exposed to the host

### Option B: Local Python Deployment

For development or when Docker isn't available, run the server directly with Python.

#### 1. Clone the Repository

```bash
git clone https://github.com/scottcrosby-securebine/juniper-mcp-v1.git
cd juniper-mcp-v1
```

#### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Prepare Device Configuration

```bash
cp devices-template.json devices.json
# Edit devices.json with your actual device information
```

#### 5. Run the Server

**For stdio transport (Claude Desktop):**

```bash
python jmcp.py -f devices.json -t stdio
```

**For streamable-http transport (VS Code, remote clients):**

```bash
python jmcp.py -f devices.json -t streamable-http -H 127.0.0.1 -p 30030
```

## Configuration

### Device Configuration

The `devices.json` file defines your Juniper network devices. See `devices-template.json` for examples.

**Minimum required fields:**
- `ip`: Device IP address or hostname
- `port`: SSH port (typically 22)
- `username`: SSH username
- `auth`: Authentication configuration

**Authentication types:**

1. **Password authentication:**
```json
{
  "my-router": {
    "ip": "192.168.1.1",
    "port": 22,
    "username": "admin",
    "auth": {
      "type": "password",
      "password": "your-password-here"
    }
  }
}
```

2. **SSH key authentication** (recommended):
```json
{
  "my-router": {
    "ip": "192.168.1.1",
    "port": 22,
    "username": "admin",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/path/to/your/private-key.pem"
    }
  }
}
```

3. **SSH config with ProxyCommand** (for jump hosts):
```json
{
  "my-router": {
    "ip": "192.168.1.1",
    "port": 22,
    "username": "admin",
    "ssh_config": "~/.ssh/config",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/path/to/your/private-key.pem"
    }
  }
}
```

### Environment Variables

The server supports environment variables for configuration:

- `MCP_SERVER_HOST`: Server host (default: `127.0.0.1`)
- `MCP_SERVER_PORT`: Server port (default: `30030`)
- `MCP_TRANSPORT`: Transport type (`stdio` or `streamable-http`)
- `DEVICE_CONFIG`: Path to devices.json
- `LOG_LEVEL`: Logging level (`INFO`, `DEBUG`, `ERROR`)

**Example:**

```bash
export MCP_SERVER_PORT=8080
export LOG_LEVEL=DEBUG
python jmcp.py -f devices.json -t streamable-http
```

## MCP Client Setup

### Claude Desktop

Configure Claude Desktop to use the Junos MCP Server by adding it to your Claude configuration file.

**Configuration file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**For local Python installation:**

```json
{
  "mcpServers": {
    "juniper-mcp-v1": {
      "command": "python",
      "args": [
        "/absolute/path/to/juniper-mcp-v1/jmcp.py",
        "-f",
        "/absolute/path/to/juniper-mcp-v1/devices.json",
        "-t",
        "stdio"
      ]
    }
  }
}
```

**For Docker installation:**

```json
{
  "mcpServers": {
    "juniper-mcp-v1": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/absolute/path/to/devices.json:/app/config/devices.json",
        "-v",
        "/absolute/path/to/your-ssh-key.pem:/app/keys/id_rsa:ro",
        "juniper-mcp-v1:latest"
      ]
    }
  }
}
```

**Important:**
- Use absolute paths, not relative paths or `~`
- Restart Claude Desktop after configuration changes

### VS Code

Configure VS Code with the MCP extension (e.g., Claude for VS Code) to connect to the server.

**1. Start the server with streamable-http transport:**

```bash
python jmcp.py -f devices.json -t streamable-http -H 127.0.0.1 -p 30030
```

**2. Configure VS Code MCP settings:**

Open Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Windows/Linux) and search for "MCP: Configure Servers".

Add the server configuration:

```json
{
  "mcp": {
    "servers": {
      "juniper-mcp-v1": {
        "url": "http://127.0.0.1:30030/mcp/"
      }
    }
  }
}
```

**With authentication (if configured):**

```json
{
  "mcp": {
    "servers": {
      "juniper-mcp-v1": {
        "url": "http://127.0.0.1:30030/mcp/",
        "headers": {
          "Authorization": "Bearer <YOUR_TOKEN>"
        }
      }
    }
  }
}
```

## Security Best Practices

### 1. Protect Sensitive Files

Never commit these files to version control:
- `devices.json` (contains credentials)
- `.tokens` (contains authentication tokens)
- SSH private keys

The `.gitignore` file is configured to exclude these automatically.

### 2. Use SSH Key Authentication

Prefer SSH key authentication over passwords:
- More secure
- Supports key rotation
- Can use passphrases for additional security

### 3. Restrict Network Access

- Run streamable-http server behind a reverse proxy with HTTPS in production
- Use firewall rules to restrict access to the MCP server port
- Consider VPN access for remote clients

### 4. Token-Based Authentication

For streamable-http transport, generate authentication tokens:

```bash
python jmcp_token_manager.py generate --id "my-client" --description "My VS Code instance"
```

Store tokens securely and rotate them regularly.

### 5. File Permissions

Ensure proper permissions on sensitive files:

```bash
chmod 600 devices.json
chmod 600 ~/.ssh/id_rsa
chmod 600 .tokens
```

### 6. Regular Updates

Keep the server and dependencies updated:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Troubleshooting

### Server Won't Start

**Check Python version:**
```bash
python --version  # Should be 3.10 or higher
```

**Check dependencies:**
```bash
pip install -r requirements.txt
```

**Check devices.json syntax:**
```bash
python -m json.tool devices.json
```

### Cannot Connect to Devices

**Test SSH connectivity:**
```bash
ssh -i /path/to/key.pem username@device-ip -p 22
```

**Check device configuration:**
- Verify IP address and port
- Confirm username and authentication credentials
- Ensure network connectivity

**Enable debug logging:**
```bash
export LOG_LEVEL=DEBUG
python jmcp.py -f devices.json -t stdio
```

### Claude Desktop Not Detecting Server

1. Verify configuration file location and syntax
2. Use absolute paths in configuration
3. Restart Claude Desktop completely
4. Check Claude Desktop logs (Help → View Logs)

### VS Code Cannot Connect

1. Verify server is running: `curl http://127.0.0.1:30030/mcp/`
2. Check firewall rules
3. Verify port is not in use: `lsof -i :30030`
4. Check authorization header if authentication is enabled

### Port Already in Use

**Find process using the port:**
```bash
# macOS/Linux
lsof -i :30030

# Windows
netstat -ano | findstr :30030
```

**Use a different port:**
```bash
python jmcp.py -f devices.json -t streamable-http -p 8080
```

### Docker Issues

**Container won't start:**
```bash
docker logs <container-id>
```

**Volume mount issues:**
- Use absolute paths
- Check file permissions
- Verify files exist before mounting

**Network connectivity:**
```bash
docker run --rm -it --network host juniper-mcp-v1:latest
```

---

For additional help, please refer to:
- [README.md](README.md) - General information and tool documentation
- [QUICK_START.md](QUICK_START.md) - Quick setup guide
- [GitHub Issues](https://github.com/scottcrosby-securebine/juniper-mcp-v1/issues) - Report bugs or request features
