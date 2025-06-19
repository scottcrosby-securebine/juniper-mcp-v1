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

from fastmcp import FastMCP
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config

# Setup logging
log = logging.getLogger('jmcp-server')

# Global variable for devices (parsed from JSON file)
devices = {}

# Junos MCP Server
JUNOS_MCP = 'jmcp-server'
mcp = FastMCP(name=JUNOS_MCP)


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
        'gather_facts': False
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

@mcp.tool()
def execute_junos_command(router_name: str, command: str) -> str:
    """Execute a Junos command on the router router_name

    Args:
        router_name(str): The name of the router.
        command(str): The command to execute on the router.

    Returns:
        The command output from router named router_name.

    """
    log.debug(f"Executing command {command} on router {router_name}")
    device_info = devices[router_name]
    
    try:
        connect_params = prepare_connection_params(device_info, router_name)
    except ValueError as ve:
        return f"Error: {ve}"
    
    try:
        with Device(**connect_params) as junos_device:
            junos_device.open()
            op = junos_device.cli(command, warning=False)
            return op
    except ConnectError as ce:
        return f"Connection error to {router_name}: {ce}"
    except Exception as e:
        return f"An error occurred: {e}"

@mcp.tool()
def get_junos_config(router_name: str) -> str:
    """Get the configuration of the router router_name
    
    Args:
        router_name(str): The name of the router on which to get the configuration.                

    Returns:
        The configuration of the router named router_name.
    
    """   
    return execute_junos_command(router_name, "show configuration | display inheritance | display set")

@mcp.tool()
def junos_config_diff(router_name: str, version: int) -> str:
    """Get the configuration diff or delta or patch or changes of a Junos router.
       Use this function to compare current running config against a particular version of the config.
       Its compares configuration changes with prior version of the configuration. You can specify 
       which version to compare as argument. Please use value between 1 and 49.
    
    Args:
        router_name(str): The name of the router on which to get the configuration diff.  
        version(int): Compare config against the said version. If you are not sure which 
                      version to compare against, please use value 1. This gives the config
                      diff from last commit.             

    Returns:
        The configuration diff (output of show | compare) of the router named router_name.
    
    """   
    return execute_junos_command(router_name, f"show configuration | compare rollback {version}")

@mcp.tool()
def gather_device_facts(router_name: str) -> str:  
    """Gather Junos device facts from the router router_name
        
    Args:
        router_name(str): The name of the router from which the facts need to be collected.  

    Returns:
        The gathered facts from Junos device using Junos PyEZ.
        
    """  
                    
    device_info = devices[router_name]
    try:
        connect_params = prepare_connection_params(device_info, router_name)
    except ValueError as ve:
        return f"Error: {ve}"
    
    try:
        with Device(**connect_params) as junos_device:
            facts = junos_device.facts
            facts_str = json.dumps(facts)
            return facts_str
    except ConnectError as ce:
        return f"Connection error to {router_name}: {ce}"
    except Exception as e:
        return f"An error occurred: {e}"

# Get list of routers
@mcp.tool()
def get_router_list() -> str:
    """Use this function to get list of Junos routers or Junos devices.
        
    Returns:
        The list of Junos routers or Junos devices.
    """
    log.debug("Getting list of routers")
    routers = list(devices.keys())
    routers_str = ', '.join(routers)
    return routers_str

@mcp.tool()
def load_and_commit_config(router_name: str, config_text: str, config_format: str = "set", commit_comment: str = "Configuration loaded via MCP") -> str:
    """Load and commit configuration on a Junos router
    
    Args:
        router_name(str): The name of the router on which to load and commit configuration
        config_text(str): The configuration text to load (can be set commands, text format, or XML)
        config_format(str): The format of the configuration. Options: "set", "text", "xml". Default is "set"
        commit_comment(str): Optional comment for the commit operation. Default is "Configuration loaded via MCP"
    
    Returns:
        Status message indicating success or failure of the load and commit operation
    """
    log.debug(f"Loading and committing config on router {router_name} with format {config_format}")
    device_info = devices[router_name]
    
    try:
        connect_params = prepare_connection_params(device_info, router_name)
    except ValueError as ve:
        return f"Error: {ve}"
    
    try:
        with Device(**connect_params) as junos_device:
            # Initialize configuration utility
            config_util = Config(junos_device)
            
            # Lock the configuration
            try:
                config_util.lock()
            except Exception as e:
                return f"Failed to lock configuration: {e}"
            
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
                    return f"Error: Unsupported config format '{config_format}'. Use 'set', 'text', or 'xml'"
                
                # Check for differences
                diff = config_util.diff()
                if not diff:
                    config_util.unlock()
                    return "No configuration changes detected"
                
                # Commit the configuration
                config_util.commit(comment=commit_comment)
                config_util.unlock()
                
                return f"Configuration successfully loaded and committed on {router_name}. Changes:\n{diff}"
                
            except Exception as e:
                # If anything fails, rollback and unlock
                try:
                    config_util.rollback()
                    config_util.unlock()
                except:
                    pass
                return f"Failed to load/commit configuration: {e}"
                
    except ConnectError as ce:
        return f"Connection error to {router_name}: {ce}"
    except Exception as e:
        return f"An error occurred: {e}"

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

    # Handle different transport types
    if args.transport == 'stdio':
        # For stdio transport, don't pass host/port
        mcp.run(transport=args.transport)
    else:
        mcp.run(host=args.host, port=args.port, transport=args.transport)

if __name__ == '__main__':
    main()