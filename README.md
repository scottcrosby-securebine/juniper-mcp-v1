# junos-mcp-server



## Getting started

Get the code.
```
git clone git@eng-gitlab.juniper.net:manageability/junos-mcp-server.git
pip install -r requirements.txt
cd junos-mcp-server
```
## Start Junos MCP server

```
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
```
{
  "mcpServers": {
    "jmcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["jmcp.py", "-f", "devices.json", "-t", "stdio"]
    }
  }
}

Note: Please provide absolute path for jmcp.py and devices.json file.
```

## Junos device config 

Junos MCP server supports both password based auth as well as ssh key based auth.

```
{
    "router-1": {
        "ip": "ip-addr",
        "port": "port-value",
        "username": "user",
        "auth": {
            "type": "password",
            "password": "pwd"
        }
    },
    "router-2": {
        "ip": "ip-addr",
        "port": "port-value",
        "username": "user",
        "auth": {
            "type": "ssh_key",
            "private_key_path": "/path/to/private/key.pem"
        }
    },
    "router-3": {
        "ip": "ip-addr",
        "port": "port-value",
        "username": "user",
        "auth": {
            "type": "password",
            "password": "pwd"
        }
    }
}

Note: port-value should be int.
```

## VSCode + Githubcopilot + Junos MCP server using streamable-http transport

### Start your server
```
$ python3.11 jmcp.py -f devices.json
[06/11/25 08:26:11] INFO     Starting MCP server 'jmcp-server' with transport 'streamable-http' on http://127.0.0.1:30030/mcp
INFO:     Started server process [33512]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:30030 (Press CTRL+C to quit)
```

### Point to this URL in your VSCode config
    "mcp": {
        "servers": {
            "my-junos-mcp-server": {
                "url": "http://127.0.0.1:30030/mcp/"
            }
        }
    }

Note: You can use VSCode's CMD+Shift+p to configure MCP server.





