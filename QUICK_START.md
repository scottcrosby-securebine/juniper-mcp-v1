# Junos MCP Server - Quick Start Guide

Get started with the Junos MCP Server in 5 minutes!

## Prerequisites

- Python 3.10+ or Docker
- Access to at least one Juniper device
- SSH credentials (preferably SSH key)

## Quick Setup

### Step 1: Get the Code

```bash
git clone https://github.com/scottcrosby-securebine/juniper-mcp-v1.git
cd juniper-mcp-v1
```

### Step 2: Configure Your Devices

```bash
cp devices-template.json devices.json
```

Edit `devices.json` with your device information:

```json
{
  "my-router": {
    "ip": "192.168.1.1",
    "port": 22,
    "username": "admin",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "~/.ssh/id_rsa"
    }
  }
}
```

### Step 3: Choose Your Deployment Method

**Option A: Docker (Recommended)**

```bash
# Build the image
docker build -t juniper-mcp-v1:latest .

# Run the server
docker run --rm -it \
  -v $(pwd)/devices.json:/app/config/devices.json \
  -v ~/.ssh/id_rsa:/app/keys/id_rsa:ro \
  juniper-mcp-v1:latest
```

**Option B: Local Python**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python jmcp.py -f devices.json -t stdio
```

### Step 4: Connect from Your AI Assistant

**For Claude Desktop:**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

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

Restart Claude Desktop.

**For VS Code:**

```bash
# Start server with HTTP transport
python jmcp.py -f devices.json -t streamable-http -H 127.0.0.1 -p 30030
```

Then configure in VS Code (Cmd+Shift+P → "MCP: Configure Servers"):

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

### Step 5: Test It!

Ask your AI assistant:

```
"List all available Juniper devices"
"Show version information for my-router"
"Get the configuration from my-router"
"Show interface status on my-router"
```

## Available Tools

The server provides 8 tools for interacting with Juniper devices:

1. **execute_junos_command** - Run any CLI command
2. **get_junos_config** - Retrieve device configuration
3. **junos_config_diff** - Compare configuration versions
4. **render_and_apply_j2_template** - Apply Jinja2 configuration templates
5. **gather_device_facts** - Get device information and facts
6. **get_router_list** - List all configured devices
7. **load_and_commit_config** - Apply configuration changes
8. **add_device** - Dynamically add devices (VSCode only)

## Common Use Cases

### Network Operations

```
"Show BGP neighbors on my-router"
"Display OSPF status for my-router"
"Check interface errors on my-router"
"Show system alarms from my-router"
```

### Configuration Management

```
"Show me the current VLAN configuration"
"Compare the current config with rollback 1"
"Display the last 5 configuration changes"
```

### Monitoring

```
"Get CPU and memory usage from my-router"
"Show chassis hardware status"
"Display current temperature sensors"
```

## Troubleshooting

### Can't connect to devices?

**Test SSH access manually:**
```bash
ssh -i ~/.ssh/id_rsa admin@192.168.1.1
```

**Check your devices.json:**
```bash
python -m json.tool devices.json
```

### Server won't start?

**Check Python version:**
```bash
python --version  # Should be 3.10+
```

**Install/update dependencies:**
```bash
pip install -r requirements.txt
```

### Claude Desktop not seeing the server?

1. **Use absolute paths** in the config (not `~` or relative paths)
2. **Restart Claude Desktop** completely
3. **Check the config file location** is correct for your OS
4. **View logs**: Help → View Logs in Claude Desktop

### VS Code can't connect?

1. **Verify server is running:**
   ```bash
   curl http://127.0.0.1:30030/mcp/
   ```

2. **Check port availability:**
   ```bash
   lsof -i :30030  # macOS/Linux
   netstat -ano | findstr :30030  # Windows
   ```

3. **Try a different port:**
   ```bash
   python jmcp.py -f devices.json -t streamable-http -p 8080
   ```

### Port already in use?

```bash
# Find what's using the port
lsof -i :30030

# Kill the process or use a different port
python jmcp.py -f devices.json -t streamable-http -p 8080
```

### Authentication failures?

1. **For SSH keys:**
   ```bash
   # Check key permissions
   chmod 600 ~/.ssh/id_rsa
   
   # Test key manually
   ssh -i ~/.ssh/id_rsa admin@device-ip
   ```

2. **For passwords:**
   - Verify password is correct in devices.json
   - Check if device requires different auth method
   - Try SSH key instead (more secure)

## Configuration Examples

### Password Authentication

```json
{
  "router1": {
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

### SSH Key Authentication (Recommended)

```json
{
  "router1": {
    "ip": "192.168.1.1",
    "port": 22,
    "username": "admin",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/home/user/.ssh/id_rsa"
    }
  }
}
```

### Using Jump Host/Proxy

```json
{
  "remote-router": {
    "ip": "10.0.0.1",
    "port": 22,
    "username": "admin",
    "ssh_config": "~/.ssh/config",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/home/user/.ssh/id_rsa"
    }
  }
}
```

With `~/.ssh/config`:
```
Host jumphost
  HostName 192.168.1.1
  User admin
  IdentityFile ~/.ssh/id_rsa

Host remote-router
  HostName 10.0.0.1
  User admin
  ProxyCommand ssh -W %h:%p jumphost
```

### EVE-NG Devices

```json
{
  "eve-ng-device": {
    "ip": "eve-ng.example.com",
    "port": 32769,
    "username": "root",
    "auth": {
      "type": "password",
      "password": "Juniper123"
    }
  }
}
```

## Security Tips

1. **Never commit `devices.json`** - It's in `.gitignore` by default
2. **Use SSH keys** instead of passwords
3. **Set proper file permissions:**
   ```bash
   chmod 600 devices.json
   chmod 600 ~/.ssh/id_rsa
   ```
4. **Use token authentication** for streamable-http:
   ```bash
   python jmcp_token_manager.py generate --id "my-client"
   ```

## Next Steps

- **[Warp Terminal Guide](docs/WARP_TERMINAL_GUIDE.md)** - Use Warp AI to manage your devices (perfect for network engineers!)
- Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for advanced configuration
- See [README.md](README.md) for complete tool documentation
- Check [CLAUDE.md](CLAUDE.md) for developer information

## Need Help?

- Check [GitHub Issues](https://github.com/scottcrosby-securebine/juniper-mcp-v1/issues)
- Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) troubleshooting section
- Consult the Juniper PyEZ documentation

---

**Happy Network Automation! 🎉**
