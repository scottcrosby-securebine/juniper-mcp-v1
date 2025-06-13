# junos-mcp-server

A Model Context Protocol (MCP) server for Juniper Junos devices that enables LLM interactions with network equipment.

## ⚠️ Important Security Notice

> **Warning:** This server enables LLM access to your network infrastructure. Please review these security considerations carefully.

### 🔒 Security Requirements

- **Corporate Policy Compliance**: Only use this server if your company's policy allows sending data of Junos devices to LLM services.

- **Server Security**: Always secure your Junos MCP server before deployment in production environments.

- **Authentication**: Do **not** use password authentication for production deployments. We strongly recommend using SSH key-based authentication for enhanced security.

- **Deployment Strategy**: Until your MCP server is properly secured, only deploy locally for testing purposes. Do not deploy remote servers in production without proper security measures.

### 🛡️ Security Best Practices

- Use SSH key authentication instead of passwords
- Implement proper network access controls
- Monitor and log all MCP server activities
- Regular security audits and updates
- Follow your organization's security policies

## Getting started

Get the code.
```bash
git clone https://github.com/Juniper/junos-mcp-server.git
cd junos-mcp-server
pip install -r requirements.txt
```

## Start Junos MCP server

```bash
$ python3.11 jmcp.py --help
Junos MCP Server

options:
  -h, --help            show this help message and exit
  -f DEVICE_MAPPING, --device-mapping DEVICE_MAPPING
                        the name of the JSON file containing the device mapping
  -H HOST, --host HOST  Junos MCP Server host
  -t TRANSPORT, --transport TRANSPORT
                        Junos MCP Server transport
  -p PORT, --port PORT  Junos MCP Server port
```

Junos MCP server supports both streamable-http and stdio transport. Do not use --host with stdio transport.

## Config for Claude desktop [using stdio transport]

```json
{
  "mcpServers": {
    "jmcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["jmcp.py", "-f", "devices.json", "-t", "stdio"]
    }
  }
}
```

**Note:** Please provide absolute path for jmcp.py and devices.json file.

## Junos device config 

Junos MCP server supports both password based auth as well as ssh key based auth.

```json
{
    "router-1": {
        "ip": "ip-addr",
        "port": 22,
        "username": "user",
        "auth": {
            "type": "password",
            "password": "pwd"
        }
    },
    "router-2": {
        "ip": "ip-addr",
        "port": 22,
        "username": "user",
        "auth": {
            "type": "ssh_key",
            "private_key_path": "/path/to/private/key.pem"
        }
    },
    "router-3": {
        "ip": "ip-addr",
        "port": 22,
        "username": "user",
        "auth": {
            "type": "password",
            "password": "pwd"
        }
    }
}
```

**Note:** Port value should be an integer (typically 22 for SSH).

## VSCode + GitHub Copilot + Junos MCP server using streamable-http transport

### Start your server

```bash
$ python3.11 jmcp.py -f devices.json
[06/11/25 08:26:11] INFO     Starting MCP server 'jmcp-server' with transport 'streamable-http' on http://127.0.0.1:30030/mcp
INFO:     Started server process [33512]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:30030 (Press CTRL+C to quit)
```

### Point to this URL in your VSCode config

```json
{
    "mcp": {
        "servers": {
            "my-junos-mcp-server": {
                "url": "http://127.0.0.1:30030/mcp/"
            }
        }
    }
}
```

**Note:** You can use VSCode's `Cmd+Shift+P` to configure MCP server.
