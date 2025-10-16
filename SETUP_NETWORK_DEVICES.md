# Network Devices Setup Guide

This guide will help you set up your network devices configuration for the Juniper MCP Server.

## Step 1: Create Your Network Devices Directory

Choose a location for your network devices folder. This will contain your device configurations and SSH keys.

**Examples:**
- **macOS/Linux**: `/Users/yourusername/network_devices`
- **Windows**: `C:\Users\yourusername\network_devices`

```bash
mkdir -p ~/network_devices/{keys,configs}
```

## Step 2: Copy Your SSH Key

If you already have a Juniper SSH key:

```bash
cp ~/.ssh/juniper_mcp_key ~/network_devices/keys/
chmod 600 ~/network_devices/keys/juniper_mcp_key
```

**Note:** The key must have `600` permissions (readable only by the owner) for security.

## Step 3: Create devices.json

Create `~/network_devices/devices.json` with your device information:

```json
{
  "my-router": {
    "ip": "router.example.com",
    "port": 22,
    "username": "radadmin",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/app/network_devices/keys/juniper_mcp_key"
    }
  }
}
```

**Important:** Use the container path `/app/network_devices/keys/` in your JSON configuration, not your local path!

### Optional: Jump Host Configuration

If you access devices through a bastion/jump host, create `~/network_devices/configs/ssh_config`:

```sshconfig
Host *
  ServerAliveInterval 60
  ServerAliveCountMax 3
  TCPKeepAlive yes
  ConnectTimeout 10

Host bastion
  HostName bastion.example.com
  User radadmin
  IdentityFile /app/network_devices/keys/juniper_mcp_key

Host *.internal
  ProxyJump bastion
  User radadmin
  IdentityFile /app/network_devices/keys/juniper_mcp_key
```

Then add to your device configuration:

```json
{
  "my-router": {
    "ip": "router.internal",
    "port": 22,
    "username": "radadmin",
    "ssh_config": "/app/network_devices/configs/ssh_config",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/app/network_devices/keys/juniper_mcp_key"
    }
  }
}
```

## Step 4: Configure Environment Variables

Copy the example environment file:

```bash
cd juniper-mcp-v1
cp .env.example .env
```

Edit `.env` and set your path:

```bash
NETWORK_DEVICES_PATH=/Users/yourusername/network_devices
```

**Replace `/Users/yourusername/` with your actual home directory path!**

## Step 5: Build and Run

### Option A: Using docker-compose (Recommended)

**For stdio transport (Claude Desktop):**
```bash
docker compose up --build
```

**For HTTP transport (VS Code):**
```bash
docker compose -f docker-compose.http.yml up --build
```

### Option B: Using docker run directly

```bash
docker build -t junos-mcp-server:latest .

docker run --rm -it \
  -v ${NETWORK_DEVICES_PATH}:/app/network_devices:ro \
  junos-mcp-server:latest
```

## Verification

Once the server starts, verify the mount:

```bash
# In another terminal
docker exec -it junos-mcp-server ls -l /app/network_devices
docker exec -it junos-mcp-server ls -l /app/network_devices/keys
```

You should see your `devices.json` and the `keys/` directory.

## Troubleshooting

### Permission Denied on SSH Key

```bash
chmod 600 ~/network_devices/keys/juniper_mcp_key
```

### Cannot Find devices.json

Verify your `NETWORK_DEVICES_PATH` in `.env` points to the correct directory and contains `devices.json`.

### Connection Errors

1. Test SSH connectivity manually:
   ```bash
   ssh -i ~/network_devices/keys/juniper_mcp_key username@device-ip
   ```

2. Check device configuration in `devices.json`
3. Verify network connectivity to devices

## Multi-User Setup

**For user "bob":**
```bash
# Bob's setup
mkdir -p /Users/bob/network_devices/{keys,configs}
cp ~/.ssh/juniper_mcp_key /Users/bob/network_devices/keys/
chmod 600 /Users/bob/network_devices/keys/juniper_mcp_key

# Bob's .env
NETWORK_DEVICES_PATH=/Users/bob/network_devices
```

**For user "alice":**
```bash
# Alice's setup
mkdir -p /Users/alice/network_devices/{keys,configs}
cp ~/.ssh/juniper_mcp_key /Users/alice/network_devices/keys/
chmod 600 /Users/alice/network_devices/keys/juniper_mcp_key

# Alice's .env
NETWORK_DEVICES_PATH=/Users/alice/network_devices
```

Each user maintains their own isolated configuration!

## Next Steps

- See [README.md](README.md) for complete documentation
- See [QUICK_START.md](QUICK_START.md) for quick setup
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment
