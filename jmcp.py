###
# Copyright (c) 1999-2025, Juniper Networks Inc.
#
#  All rights reserved.
#
#  License: Apache 2.0
#
#  THIS SOFTWARE IS PROVIDED BY Juniper Networks Inc. ''AS IS'' AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL Juniper Networks Inc. BE LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###

import argparse
import logging
import os
import json
import sys
import signal
from typing import Any, Sequence

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger('jmcp-server')

# Global variable for devices (parsed from JSON file)
devices = {}

# Junos MCP Server
JUNOS_MCP = 'jmcp-server'



def prepare_connection_params(device_info: dict, router_name: str) -> dict:
    """Prepare connection parameters based on authentication type
    
    Args:
        device_info(dict): Device configuration dictionary
        router_name(str): Name of the router (used for error messages)
    
    Returns:
        dict: Connection parameters for Junos Device
    
    Raises:
        ValueError: If authentication configuration is invalid
    """
    # Base connection parameters
    connect_params = {
        'host': device_info['ip'],
        'port': device_info['port'],
        'user': device_info['username'],
        'gather_facts': False,
        'timeout': 360  # Default timeout of 360 seconds
    }
    
    # Handle different authentication methods
    if 'auth' in device_info:
        auth_config = device_info['auth']
        if auth_config['type'] == 'password':
            connect_params['password'] = auth_config['password']
        elif auth_config['type'] == 'ssh_key':
            connect_params['ssh_private_key_file'] = auth_config['private_key_path']
        else:
            raise ValueError(f"Unsupported auth type '{auth_config['type']}' for {router_name}")
    elif 'password' in device_info:
        # Backward compatibility with old format
        connect_params['password'] = device_info['password']
    else:
        raise ValueError(f"No valid authentication method found for {router_name}")
    
    return connect_params

def _run_junos_cli_command(router_name: str, command: str, timeout: int = 360) -> str:
    """Internal helper to connect and run a Junos CLI command."""
    log.debug(f"Executing command {command} on router {router_name} with timeout {timeout}s (internal)")
    device_info = devices[router_name]
    try:
        connect_params = prepare_connection_params(device_info, router_name)
    except ValueError as ve:
        return f"Error: {ve}"
    try:
        with Device(**connect_params) as junos_device:
            junos_device.open()
            junos_device.timeout = timeout
            op = junos_device.cli(command, warning=False)
            return op
    except ConnectError as ce:
        return f"Connection error to {router_name}: {ce}"
    except Exception as e:
        return f"An error occurred: {e}"


def validate_token_from_file(token: str) -> bool:
    """Validate if a token exists in the .tokens file"""
    try:
        if not os.path.exists(".tokens"):
            return False
        
        with open(".tokens", 'r') as f:
            tokens = json.load(f)
        
        for token_data in tokens.values():
            if token_data.get('token') == token:
                return True
        
        return False
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return False


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Middleware to check Bearer token authentication for streamable-http"""
    
    def __init__(self, app, auth_enabled: bool = True):
        super().__init__(app)
        self.auth_enabled = auth_enabled
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth if disabled (for stdio transport)
        if not self.auth_enabled:
            return await call_next(request)
        
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing or invalid Authorization header"}, 
                status_code=401
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Validate token against .tokens file
        if not validate_token_from_file(token):
            log.warning(f"Invalid token attempt from {request.client.host if request.client else 'unknown'}")
            return JSONResponse(
                {"error": "Invalid token"}, 
                status_code=401
            )
        
        log.debug("Token validation successful")
        return await call_next(request)


def create_mcp_server() -> Server:
    """Create and configure the MCP server with all tools"""
    app = Server(JUNOS_MCP)
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
        """Handle tool calls"""
        if name == "execute_junos_command":
            router_name = arguments.get("router_name", "")
            command = arguments.get("command", "")
            timeout = arguments.get("timeout", 360)
            
            if router_name not in devices:
                result = f"Router {router_name} not found in the device mapping."
            else:
                log.debug(f"Executing command {command} on router {router_name} with timeout {timeout}s")
                result = _run_junos_cli_command(router_name, command, timeout)
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_junos_config":
            router_name = arguments.get("router_name", "")
            
            if router_name not in devices:
                result = f"Router {router_name} not found in the device mapping."
            else:
                log.debug(f"Getting configuration from router {router_name}")
                result = _run_junos_cli_command(router_name, "show configuration | display inheritance no-comments | no-more")
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "junos_config_diff":
            router_name = arguments.get("router_name", "")
            version = arguments.get("version", 1)
            
            if router_name not in devices:
                result = f"Router {router_name} not found in the device mapping."
            else:
                log.debug(f"Getting configuration diff from router {router_name} for version {version}")
                result = _run_junos_cli_command(router_name, f"show configuration | compare rollback {version}")
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "gather_device_facts":
            router_name = arguments.get("router_name", "")
            timeout = arguments.get("timeout", 360)
            
            if router_name not in devices:
                result = f"Router {router_name} not found in the device mapping."
            else:
                log.debug(f"Getting facts from router {router_name} with timeout {timeout}s")
                device_info = devices[router_name]
                try:
                    connect_params = prepare_connection_params(device_info, router_name)
                    connect_params['timeout'] = timeout
                except ValueError as ve:
                    result = f"Error: {ve}"
                else:
                    try:
                        with Device(**connect_params) as junos_device:
                            facts = junos_device.facts
                            # Convert _FactCache to a regular dict
                            facts_dict = dict(facts)
                            
                            # Custom JSON encoder to handle version_info and other complex objects
                            def json_serializer(obj):
                                if hasattr(obj, '_asdict'):  # Named tuples like version_info
                                    return obj._asdict()
                                elif hasattr(obj, '__dict__'):  # Objects with __dict__
                                    return obj.__dict__
                                else:
                                    return str(obj)
                            
                            result = json.dumps(facts_dict, indent=2, default=json_serializer)
                    except ConnectError as ce:
                        result = f"Connection error to {router_name}: {ce}"
                    except Exception as e:
                        result = f"An error occurred: {e}"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_router_list":
            log.debug("Getting list of routers")
            routers = list(devices.keys())
            result = ', '.join(routers)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "load_and_commit_config":
            router_name = arguments.get("router_name", "")
            config_text = arguments.get("config_text", "")
            config_format = arguments.get("config_format", "set")
            commit_comment = arguments.get("commit_comment", "Configuration loaded via MCP")
            
            if router_name not in devices:
                result = f"Router {router_name} not found in the device mapping."
            else:
                log.debug(f"Loading and committing config on router {router_name} with format {config_format}")
                device_info = devices[router_name]
                
                try:
                    connect_params = prepare_connection_params(device_info, router_name)
                except ValueError as ve:
                    result = f"Error: {ve}"
                else:
                    try:
                        with Device(**connect_params) as junos_device:
                            # Initialize configuration utility
                            config_util = Config(junos_device)
                            
                            # Lock the configuration
                            try:
                                config_util.lock()
                            except Exception as e:
                                result = f"Failed to lock configuration: {e}"
                            else:
                                try:
                                    # Load the configuration based on format
                                    if config_format.lower() == "set":
                                        config_util.load(config_text, format='set')
                                    elif config_format.lower() == "text":
                                        config_util.load(config_text, format='text')
                                    elif config_format.lower() == "xml":
                                        config_util.load(config_text, format='xml')
                                    else:
                                        config_util.unlock()
                                        result = f"Error: Unsupported config format '{config_format}'. Use 'set', 'text', or 'xml'"
                                    
                                    if 'result' not in locals():
                                        # Check for differences
                                        diff = config_util.diff()
                                        if not diff:
                                            config_util.unlock()
                                            result = "No configuration changes detected"
                                        else:
                                            # Commit the configuration
                                            config_util.commit(comment=commit_comment)
                                            config_util.unlock()
                                            result = f"Configuration successfully loaded and committed on {router_name}. Changes:\n{diff}"
                                            
                                except Exception as e:
                                    # If anything fails, rollback and unlock
                                    try:
                                        config_util.rollback()
                                        config_util.unlock()
                                    except:
                                        pass
                                    result = f"Failed to load/commit configuration: {e}"
                                    
                    except ConnectError as ce:
                        result = f"Connection error to {router_name}: {ce}"
                    except Exception as e:
                        result = f"An error occurred: {e}"
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        """List available resources - none for this server"""
        return []
    
    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        """List available prompts - none for this server"""
        return []
    
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="execute_junos_command",
                description="Execute a Junos command on the router",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "router_name": {"type": "string", "description": "The name of the router"},
                        "command": {"type": "string", "description": "The command to execute on the router"},
                        "timeout": {"type": "integer", "description": "Command timeout in seconds", "default": 360}
                    },
                    "required": ["router_name", "command"]
                }
            ),
            types.Tool(
                name="get_junos_config",
                description="Get the configuration of the router",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "router_name": {"type": "string", "description": "The name of the router"}
                    },
                    "required": ["router_name"]
                }
            ),
            types.Tool(
                name="junos_config_diff",
                description="Get the configuration diff against a rollback version",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "router_name": {"type": "string", "description": "The name of the router"},
                        "version": {"type": "integer", "description": "Rollback version to compare against (1-49)", "default": 1}
                    },
                    "required": ["router_name"]
                }
            ),
            types.Tool(
                name="gather_device_facts",
                description="Gather Junos device facts from the router",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "router_name": {"type": "string", "description": "The name of the router"},
                        "timeout": {"type": "integer", "description": "Connection timeout in seconds", "default": 360}
                    },
                    "required": ["router_name"]
                }
            ),
            types.Tool(
                name="get_router_list",
                description="Get list of available Junos routers",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="load_and_commit_config",
                description="Load and commit configuration on a Junos router",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "router_name": {"type": "string", "description": "The name of the router"},
                        "config_text": {"type": "string", "description": "The configuration text to load"},
                        "config_format": {"type": "string", "description": "Format: set, text, or xml", "default": "set"},
                        "commit_comment": {"type": "string", "description": "Commit comment", "default": "Configuration loaded via MCP"}
                    },
                    "required": ["router_name", "config_text"]
                }
            )
        ]

    return app


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Junos MCP Server")
    
    # Add the arguments
    parser.add_argument('-f', '--device-mapping', default="devices.json", type=str, help='the name of the JSON file containing the device mapping')
    parser.add_argument('-H', '--host', default="127.0.0.1", type=str, help='Junos MCP Server host')
    parser.add_argument('-t', '--transport', default="streamable-http", type=str, help='Junos MCP Server transport')
    parser.add_argument('-p', '--port', default=30030, type=int, help='Junos MCP Server port')

    
    # Parse the arguments
    args = parser.parse_args()
    global devices
    
    # Check if authentication should be enabled
    auth_enabled = False
    if args.transport != 'stdio':
        # For non-stdio transports, check if we have tokens configured
        if os.path.exists(".tokens"):
            try:
                with open(".tokens", 'r') as f:
                    tokens = json.load(f)
                    if tokens:  # If tokens exist, enable auth
                        auth_enabled = True
                        log.info("Token-based authentication enabled")
                        log.info("Clients must send 'Authorization: Bearer <token>' header")
                        log.info("Use jmcp_token_manager.py to manage tokens")
                    else:
                        log.warning("Empty .tokens file found - server is open to all clients")
            except (json.JSONDecodeError, FileNotFoundError):
                log.warning("Invalid .tokens file - server is open to all clients")
        else:
            log.warning("No .tokens file found - server is open to all clients")
            log.info("Create tokens using: python jmcp_token_manager.py generate --id <token-id>")
    else:
        log.info("stdio transport - no authentication required")
    
    try:
        with open(args.device_mapping, 'r') as f:
            devices = json.load(f)
    except FileNotFoundError:
        print(f"File {args.device_mapping} not found.")
        devices = {}
        raise
    except json.JSONDecodeError:
        print(f"File {args.device_mapping} is not a valid JSON file.")
        devices = {}
        raise

    # Set up signal handler for clean shutdown
    def signal_handler(sig, frame):
        print("\nShutting down MCP server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create MCP server
    mcp_server = create_mcp_server()

    # Run with the specified transport
    try:
        if args.transport == 'stdio':
            # For stdio transport, run directly
            from mcp.server.stdio import stdio_server
            from mcp.server.models import InitializationOptions, ServerCapabilities
            
            async def run_stdio():
                async with stdio_server() as (read_stream, write_stream):
                    init_options = InitializationOptions(
                        server_name=JUNOS_MCP,
                        server_version="1.0.0",
                        capabilities=ServerCapabilities()
                    )
                    await mcp_server.run(
                        read_stream,
                        write_stream,
                        init_options
                    )
            
            anyio.run(run_stdio)
        elif args.transport == 'streamable-http':
            # For streamable-http, create Starlette app with session manager
            async def run_streamable_http():
                session_manager = StreamableHTTPSessionManager(
                    app=mcp_server,
                    event_store=None,  # No persistence
                    stateless=True
                )
                
                # ASGI handler
                async def handle_streamable_http(scope, receive, send):
                    await session_manager.handle_request(scope, receive, send)
                
                # Create middleware stack
                middleware = []
                if auth_enabled:
                    middleware.append(Middleware(BearerTokenMiddleware, auth_enabled=True))
                
                # Create Starlette app
                async def lifespan(app):
                    async with session_manager.run():
                        log.info(f"Streamable HTTP server started on http://{args.host}:{args.port}")
                        yield
                        log.info("Server shutting down...")
                
                starlette_app = Starlette(
                    routes=[Mount("/mcp", app=handle_streamable_http)],
                    middleware=middleware,
                    lifespan=lifespan
                )
                
                # Run with uvicorn
                import uvicorn
                config = uvicorn.Config(
                    starlette_app,
                    host=args.host,
                    port=args.port,
                    log_level="info"
                )
                server = uvicorn.Server(config)
                await server.serve()
            
            anyio.run(run_streamable_http)
        else:
            log.error(f"Unsupported transport: {args.transport}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()