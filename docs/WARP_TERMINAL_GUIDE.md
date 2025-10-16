# Warp Terminal Guide for Juniper MCP Server

**Using Docker MCP Gateway with Warp AI - A Complete Guide for Network Engineers**

---

## Table of Contents

- [Introduction](#introduction)
- [What is the Docker MCP Gateway?](#what-is-the-docker-mcp-gateway)
- [What is Warp AI?](#what-is-warp-ai)
- [Why Use This Setup?](#why-use-this-setup)
- [Prerequisites](#prerequisites)
- [Understanding the Architecture](#understanding-the-architecture)
- [Quick Setup Guide](#quick-setup-guide)
- [Adding the Juniper MCP Server](#adding-the-juniper-mcp-server)
- [Configuring Warp Terminal](#configuring-warp-terminal)
- [Using Warp AI Features](#using-warp-ai-features)
- [Common Network Operations](#common-network-operations)
- [Managing Multiple MCP Servers](#managing-multiple-mcp-servers)
- [Troubleshooting with Warp AI](#troubleshooting-with-warp-ai)
- [Warp AI Prompt Library](#warp-ai-prompt-library)
- [Best Practices and Security](#best-practices-and-security)
- [Warp Terminal Tips and Tricks](#warp-terminal-tips-and-tricks)

---

## Introduction

Welcome, network engineers! This guide will help you set up and use **Docker MCP Gateway** with **Warp Terminal's AI** to manage your Juniper network devices.

**No programming experience required!** This guide uses a modern approach where:
- One gateway manages all your MCP servers
- Warp AI helps you understand every command
- You can add multiple network tools (not just Juniper!)
- Everything runs in Docker containers for easy management

### What You'll Learn

1. How to set up the Docker MCP Gateway (the "master controller")
2. How to add the Juniper MCP server to the gateway
3. How to connect Warp Terminal to manage your devices
4. How to use Warp AI to help with daily network operations
5. How to add other tools (firewalls, security tools, etc.) to the same gateway

---

## What is the Docker MCP Gateway?

Think of the Docker MCP Gateway as a **master controller** that manages all your AI-powered network tools.

### Simple Analogy

Imagine you have multiple remote controls for different devices:
- One for Juniper routers
- One for your firewall
- One for your virtualization servers
- One for security scanning tools

The Docker MCP Gateway is like a **universal remote** that:
- Manages all these tools in one place
- Lets Warp AI talk to all of them through one connection
- Makes it easy to add or remove tools
- Keeps everything organized

### Without Gateway (Old Way)

```
Warp Terminal → Direct connection to Juniper MCP Server
                (Have to configure each server separately)
```

### With Gateway (New Way - What You'll Use)

```
Warp Terminal
    ↓ (One connection)
Docker MCP Gateway
    ├─→ Juniper MCP Server (manages routers/switches)
    ├─→ OPNsense MCP Server (manages firewalls)
    ├─→ Proxmox MCP Server (manages VMs)
    └─→ Security Tools Server (penetration testing)
```

**Benefits:**
- ✅ One Warp configuration for everything
- ✅ Easy to add new tools
- ✅ All tools available in one AI conversation
- ✅ Centralized management
- ✅ No need to restart Warp when adding tools

---

## What is Warp AI?

Warp is a modern terminal with a built-in AI assistant. It's like having an experienced network engineer available 24/7 to:

- **Explain commands** before you run them
- **Help troubleshoot** when things go wrong
- **Generate commands** for complex tasks
- **Interpret output** from your network devices
- **Provide guidance** for unfamiliar procedures

### Key Warp Features for Network Engineers

1. **AI Command Help** (`Ctrl+Shift+Space`): Ask AI about anything
2. **Command Explanations**: Highlight any command and ask "What does this do?"
3. **Error Diagnosis**: When something fails, AI explains why
4. **Output Interpretation**: AI explains complex device output
5. **Command History**: Searchable history with `Ctrl+R`

---

## Why Use This Setup?

### For Network Engineers Who Aren't Programmers

1. **Simplified Management**: One setup manages all your network tools
2. **AI Assistance**: Warp AI helps with Docker and configuration commands
3. **No Manual Configs**: Add servers by editing simple YAML files
4. **Easy Troubleshooting**: Warp AI diagnoses Docker and network issues
5. **Scalable**: Start with Juniper, add firewalls and security tools later

### Real-World Example

**Scenario**: You want to check your Juniper router, then verify your firewall rules, then scan for vulnerabilities.

**Without Gateway**: 
- Open three different terminals
- Connect to three different tools
- Switch between them constantly

**With Gateway**:
- Open one Warp terminal
- Talk to Warp AI: "Check Juniper router health, then firewall rules, then run security scan"
- AI coordinates with all tools through the gateway

---

## Prerequisites

### System Requirements

- **Operating System**: macOS with Apple Silicon (M1/M2/M3) or Intel
- **Docker Desktop**: Version 4.27.0 or newer ([Download here](https://www.docker.com/products/docker-desktop/))
- **Warp Terminal**: Latest version ([Download here](https://www.warp.dev/))
- **Disk Space**: At least 5GB free for Docker images

### Network Requirements

- **SSH Access**: To your Juniper devices (port 22)
- **SSH Keys** (Recommended): For secure authentication  
- **Network Connectivity**: From your Mac to your Juniper devices

### Knowledge Requirements

- **None!** This guide assumes you're new to:
  - Docker containers
  - MCP servers
  - YAML configuration files
  - Command-line tools

Warp AI will help you learn as you go!

---

## Understanding the Architecture

Let's understand how all the pieces fit together.

### The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                       Your Mac                              │
│                                                             │
│  ┌─────────────────┐                                       │
│  │  Warp Terminal  │                                       │
│  │  (with AI)      │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           │ stdio connection                                │
│           ↓                                                 │
│  ┌────────────────────────────────────────────────┐       │
│  │     Docker MCP Gateway Container               │       │
│  │     (The Master Controller)                    │       │
│  │                                                 │       │
│  │  Manages all your MCP servers:                │       │
│  │  • Reads catalog files (custom.yaml)          │       │
│  │  • Starts/stops containers                     │       │
│  │  • Routes AI requests                          │       │
│  └─────────┬──────────────────────────────────────┘       │
│            │                                                │
│            ├──────────────┬──────────────┬────────────┐   │
│            ↓              ↓              ↓            ↓   │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────┐ ┌────────┐│
│  │   Juniper    │ │   OPNsense   │ │ Proxmox │ │ Kali   ││
│  │  MCP Server  │ │  MCP Server  │ │   MCP   │ │  Tools ││
│  │              │ │              │ │  Server │ │        ││
│  └──────┬───────┘ └──────┬───────┘ └────┬────┘ └────────┘│
│         │                │               │                 │
└─────────┼────────────────┼───────────────┼─────────────────┘
          │                │               │
          ↓                ↓               ↓
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Juniper  │    │ OPNsense │    │ Proxmox  │
    │ Routers  │    │ Firewall │    │ VMs      │
    └──────────┘    └──────────┘    └──────────┘
```

### Key Components

1. **Warp Terminal**: Where you type commands and ask AI for help
2. **Docker MCP Gateway**: The container that manages everything
3. **MCP Servers**: Individual containers for different tasks (Juniper, firewall, etc.)
4. **Catalog Files**: YAML files that tell the gateway what servers exist
5. **Network Devices**: Your actual routers, switches, firewalls

### Configuration Files Explained

Your Docker MCP setup uses several files:

```
~/.docker/mcp/
├── catalogs/
│   ├── docker-mcp.yaml      # Official Docker MCP servers (GitHub, AWS, etc.)
│   └── custom.yaml           # YOUR custom servers (Juniper, OPNsense, etc.)
├── config.yaml               # Server-specific configurations
├── registry.yaml             # List of all registered servers
└── tools.yaml                # Tool-specific settings (usually empty)
```

**You'll mainly work with `custom.yaml`** to add your Juniper MCP server!

---

## Quick Setup Guide

Let's get everything set up step-by-step. Warp AI will help you at each stage.

### Step 1: Install Docker Desktop

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and open Docker Desktop
3. Wait for Docker to start (you'll see a green "Running" status)

**Verify Docker is running:**

```bash
docker --version
```

**Ask Warp AI if you get an error:**
```
"I got this error when checking Docker version: [paste error]. How do I fix it?"
```

### Step 2: Create the MCP Directory Structure

This creates all the folders you need:

```bash
mkdir -p ~/.docker/mcp/catalogs
mkdir -p ~/.docker/mcp
```

**Ask Warp AI:**
```
"What did these mkdir commands just do?"
```

### Step 3: Create the Configuration Files

Let's create empty configuration files that the gateway needs:

```bash
# Create empty config files
touch ~/.docker/mcp/config.yaml
touch ~/.docker/mcp/registry.yaml
touch ~/.docker/mcp/tools.yaml
```

**Explanation**: These are configuration files the gateway will use. We'll add content later.

### Step 4: Create Your Custom Catalog File

This is where you'll define your Juniper MCP server and any other tools:

```bash
nano ~/.docker/mcp/catalogs/custom.yaml
```

**Press `Ctrl+X`, then `Y`, then `Enter` to save and exit** (we'll add content in the next section).

### Step 5: Pull the Docker MCP Gateway Image

Download the gateway container:

```bash
docker pull docker/mcp-gateway
```

**Ask Warp AI while it's downloading:**
```
"What is Docker doing right now when it says 'Pull complete'?"
```

**Congratulations!** The basic setup is complete. Next, we'll add the Juniper MCP server.

---

## Adding the Juniper MCP Server

Now let's add the Juniper MCP server to your gateway so you can manage your routers.

### Step 1: Build the Juniper MCP Server Docker Image

First, get the Juniper MCP server code:

```bash
cd ~/Documents
git clone https://github.com/Juniper/junos-mcp-server.git
cd junos-mcp-server
```

**Build the Docker image:**

```bash
docker build -t junos-mcp-server:latest .
```

**Ask Warp AI while building:**
```
"Explain what 'docker build' is doing in simple terms"
```

### Step 2: Prepare Your Device Configuration

Create a directory for your network device configurations:

```bash
mkdir -p ~/network_devices/keys
mkdir -p ~/network_devices/configs
```

**Create your devices configuration file:**

```bash
nano ~/network_devices/devices.json
```

**Add your router information** (example):

```json
{
  "my-router": {
    "ip": "192.168.1.1",
    "port": 22,
    "username": "admin",
    "auth": {
      "type": "ssh_key",
      "private_key_path": "/app/network_devices/keys/id_rsa"
    }
  }
}
```

**💡 Important**: Use the path `/app/network_devices/keys/` because that's where it will be inside the Docker container!

**Copy your SSH key** to the keys folder:

```bash
cp ~/.ssh/id_rsa ~/network_devices/keys/
chmod 600 ~/network_devices/keys/id_rsa
```

**Ask Warp AI:**
```
"Why do I need to chmod 600 my SSH key file?"
```

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Add Juniper Server to Your Custom Catalog

Edit your custom catalog:

```bash
nano ~/.docker/mcp/catalogs/custom.yaml
```

**Add this content:**

```yaml
version: 2
name: custom
displayName: Custom MCP Servers
registry:
  junos-network-manager:
    description: "Juniper network device management and automation MCP server. Provides AI-powered interface to manage Juniper routers, switches, and firewalls. Features: execute CLI commands, retrieve/modify configurations, config diffs, device facts, load/commit configs, Jinja2 templates. Supports SSH key and password authentication."
    title: "Juniper Network Device Manager"
    type: server
    dateAdded: "2025-01-16T00:00:00Z"
    image: junos-mcp-server:latest
    tools:
      - name: execute_junos_command
      - name: get_junos_config
      - name: junos_config_diff
      - name: render_and_apply_j2_template
      - name: gather_device_facts
      - name: get_router_list
      - name: load_and_commit_config
      - name: add_device
    volumes:
      - /Users/YOUR_USERNAME/network_devices:/app/network_devices:ro
    metadata:
      category: automation
      tags:
        - networking
        - juniper
        - junos
        - network-automation
      license: Apache-2.0
      owner: local
```

**⚠️ IMPORTANT**: Replace `/Users/YOUR_USERNAME/` with your actual macOS username!

**Find your username:**
```bash
echo $HOME
```

**Ask Warp AI:**
```
"Explain what the 'volumes' section does in this YAML file"
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Register the Server in the Registry

Edit the registry file:

```bash
nano ~/.docker/mcp/registry.yaml
```

**Add this:**

```yaml
registry:
  junos-network-manager:
    ref: ""
```

**Save**: `Ctrl+X`, `Y`, `Enter`

**Congratulations!** The Juniper MCP server is now registered with your gateway!

---

## Configuring Warp Terminal

Now let's connect Warp Terminal to your Docker MCP Gateway.

### Step 1: Open Warp Settings

1. Open Warp Terminal
2. Press `Cmd+,` (Command + Comma) to open Settings
3. Click on **Features** in the left sidebar
4. Scroll down to **Model Context Protocol (MCP)**
5. Click **Edit Config** or **Add Server**

### Step 2: Add the Gateway Configuration

Add this configuration (you can click **Edit as JSON** to paste directly):

```json
{
  "mcp-toolkit-gateway": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-v",
      "/var/run/docker.sock:/var/run/docker.sock",
      "-v",
      "/Users/YOUR_USERNAME/.docker/mcp:/mcp",
      "docker/mcp-gateway",
      "--catalog=/mcp/catalogs/docker-mcp.yaml",
      "--catalog=/mcp/catalogs/custom.yaml",
      "--config=/mcp/config.yaml",
      "--registry=/mcp/registry.yaml",
      "--tools-config=/mcp/tools.yaml",
      "--transport=stdio"
    ],
    "env": {},
    "working_directory": null
  }
}
```

**⚠️ IMPORTANT**: Replace `YOUR_USERNAME` with your actual macOS username!

**Ask Warp AI:**
```
"Explain what each argument in this Docker command does"
```

### Step 3: Save and Restart Warp

1. Click **Save**
2. Restart Warp Terminal
3. Look for the MCP icon (usually bottom-left or in the command bar)

### Step 4: Verify the Connection

In Warp, ask the AI:

```
"List all available MCP servers"
```

or

```
"What Juniper routers are available?"
```

You should see your `junos-network-manager` server listed!

**If you don't see it, ask Warp AI:**
```
"The MCP gateway isn't showing my Juniper server. How do I troubleshoot this?"
```

---

## Using Warp AI Features

Now that everything is connected, let's learn how to use Warp AI effectively.

### Feature 1: Command Explanations

**Scenario**: You see a Docker command but don't understand it.

**How to use:**
1. Highlight the command text in Warp
2. Press `Ctrl+Shift+Space` or click the AI button
3. Type: "Explain this command"

**Example:**

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock
```

**Ask Warp AI:**
```
"What does -v /var/run/docker.sock:/var/run/docker.sock do?"
```

### Feature 2: Error Diagnosis

**Scenario**: A command fails with an error.

**Example error:**

```
Error: Cannot connect to router: Permission denied (publickey)
```

**Ask Warp AI:**
```
"I got this error: Permission denied (publickey). This is for SSH to my Juniper router. What's wrong and how do I fix it?"
```

Warp AI will explain it's an SSH key problem and suggest:
- Checking the key path in devices.json
- Verifying key permissions (should be 600)
- Testing SSH manually

### Feature 3: Generating Commands

**Scenario**: You want to do something but don't know the command.

**Ask Warp AI:**
```
"How do I check if my Docker containers are running?"
```

Warp AI will suggest:
```bash
docker ps
```

**Then ask:**
```
"What does 'docker ps' show me?"
```

### Feature 4: Interpreting Junos Output

**Scenario**: You run a command through the MCP server and get complex output.

**Example**: You ask Warp AI:
```
"Show me interface status for my-router"
```

And get:

```
Physical interface: ge-0/0/0, Enabled, Physical link is Up
  Interface index: 148, SNMP ifIndex: 526
  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps
  ...
```

**Ask Warp AI:**
```
"Explain this Junos interface output in simple terms. Is everything healthy?"
```

### Feature 5: Configuration Validation

**Before making configuration changes**, always ask Warp AI:

```
"I'm about to change my router's BGP configuration. What should I backup first and what are the risks?"
```

Warp AI will remind you to:
- Backup current configuration
- Test in lab if possible
- Have a rollback plan

---

## Common Network Operations

Here are practical workflows for everyday tasks, using Warp AI to help.

### Workflow 1: Check Device Health

**Goal**: Quickly verify your router is healthy.

**Step 1 - Ask Warp AI for guidance:**

```
"I want to check if my Juniper router is healthy. What should I look at?"
```

**Step 2 - List your routers:**

```
"List all available routers in the MCP server"
```

**Step 3 - Check system status:**

```
"Show system alarms and uptime for my-router"
```

**Step 4 - Interpret the results:**

**Copy the output and ask Warp AI:**
```
"Review this 'show chassis alarms' output. Are there any issues I should worry about?"
```

### Workflow 2: Verify Interface Status

**Goal**: Check if all interfaces are up and running.

**Step 1 - Get interface summary:**

```
"Show interface status for my-router"
```

**Step 2 - Ask Warp AI to interpret:**

```
"Look at this interface output. Which interfaces are down and why might that be?"
```

**Step 3 - Get detailed info on a specific interface:**

```
"Show detailed status for interface ge-0/0/0 on my-router"
```

### Workflow 3: Backup Configuration

**Goal**: Save current router configuration before making changes.

**Step 1 - Get the configuration:**

```
"Get the full configuration from my-router"
```

**Step 2 - Save to a file:**

**Ask Warp AI:**
```
"How do I save the configuration output to a file with today's date in the filename?"
```

Warp AI will suggest something like:
```bash
# The output will be shown in the terminal, then:
cat > my-router-config-$(date +%Y%m%d).txt
# Paste the config
# Press Ctrl+D to save
```

**Step 3 - Verify the backup:**

```bash
ls -lh my-router-config-*.txt
```

### Workflow 4: Compare Configurations

**Goal**: See what changed between configuration versions.

**Step 1 - Use the config diff tool:**

```
"Show configuration differences between current and rollback 1 for my-router"
```

**Step 2 - Ask Warp AI to explain:**

```
"Explain what changed in this configuration diff. Is this a normal change?"
```

### Workflow 5: Check BGP Neighbors

**Goal**: Verify BGP sessions are working.

**Step 1 - View BGP summary:**

```
"Show BGP neighbor status on my-router"
```

or

```
"Execute 'show bgp summary' on my-router"
```

**Step 2 - Understand the output:**

**Ask Warp AI:**
```
"Explain these BGP neighbor states. Is 'Established' good? What about 'Active'?"
```

**Step 3 - Troubleshoot problems:**

If a neighbor isn't established:

```
"My BGP neighbor 10.1.1.1 is in 'Active' state instead of 'Established'. What are the most common causes?"
```

### Workflow 6: Monitor OSPF

**Goal**: Check OSPF neighbor status and routes.

**Step 1 - Check OSPF neighbors:**

```
"Show OSPF neighbors on my-router"
```

**Step 2 - Interpret the output:**

```
"What should I see in 'show ospf neighbor' if OSPF is working correctly?"
```

**Step 3 - Check OSPF routes:**

```
"Show OSPF routes on my-router"
```

### Workflow 7: Review System Logs

**Goal**: Check for recent errors or warnings.

**Step 1 - View recent logs:**

```
"Show the last 50 log messages from my-router"
```

**Step 2 - Filter for errors:**

```
"Are there any error or critical messages in these logs?"
```

**Step 3 - Investigate specific errors:**

**Copy an error message and ask:**
```
"What does this Junos error mean: [paste error]? How serious is it and how do I fix it?"
```

---

## Managing Multiple MCP Servers

One of the biggest advantages of the Docker MCP Gateway is managing multiple servers. Here's how to add more tools beyond Juniper.

### Understanding Multi-Server Setup

Your `custom.yaml` can contain multiple servers:

```yaml
version: 2
name: custom
displayName: Custom MCP Servers
registry:
  junos-network-manager:
    # Juniper configuration here
  
  opnsense-mcp:
    # Firewall management here
  
  proxmox-mcp:
    # VM management here
  
  kali-security-tools:
    # Security scanning here
```

### Example: Adding a Second Server

Let's say you want to add OPNsense firewall management.

**Step 1 - Build or pull the OPNsense MCP server:**

```bash
# Example - adjust based on actual server
docker pull opnsense-mcp-server:latest
```

**Step 2 - Add to custom.yaml:**

```bash
nano ~/.docker/mcp/catalogs/custom.yaml
```

Add under `registry:` (after your junos-network-manager section):

```yaml
  opnsense-mcp:
    description: "OPNsense firewall management server"
    title: "OPNsense Firewall Manager"
    type: server
    dateAdded: "2025-01-16T00:00:00Z"
    image: opnsense-mcp-server:latest
    tools:
      - name: list_firewall_rules
      - name: get_system_status
    volumes:
      - /Users/YOUR_USERNAME/network_devices:/config:ro
    metadata:
      category: security
      tags:
        - firewall
        - opnsense
      license: MIT
      owner: local
```

**Step 3 - Add to registry:**

```bash
nano ~/.docker/mcp/registry.yaml
```

Add:

```yaml
  opnsense-mcp:
    ref: ""
```

**Step 4 - Restart Warp Terminal**

Your new server will be available!

### Using Multiple Servers Together

**Example conversation with Warp AI:**

```
"Show me the health of my Juniper router, then check my OPNsense firewall rules for any blocks to that router's IP"
```

Warp AI will:
1. Connect to Juniper MCP server to check router health
2. Connect to OPNsense MCP server to check firewall rules
3. Correlate the information and present a unified answer

---

## Troubleshooting with Warp AI

When things go wrong, Warp AI is your troubleshooting partner.

### Problem 1: Gateway Won't Start

**Error message:**

```
Error: Cannot connect to MCP gateway
```

**Ask Warp AI:**
```
"Docker MCP gateway won't start. How do I troubleshoot this?"
```

**Step 1 - Check if Docker is running:**

```bash
docker ps
```

**Step 2 - Check gateway logs:**

**Ask Warp AI:**
```
"How do I see Docker container logs?"
```

Warp AI will suggest:
```bash
docker logs $(docker ps -q --filter ancestor=docker/mcp-gateway)
```

### Problem 2: Juniper Server Not Showing Up

**Issue**: You added the Juniper server but Warp doesn't see it.

**Step 1 - Verify the configuration:**

**Ask Warp AI:**
```
"How do I check if my custom.yaml file is valid YAML syntax?"
```

```bash
cat ~/.docker/mcp/catalogs/custom.yaml
```

**Step 2 - Check if the image exists:**

```bash
docker images | grep junos-mcp-server
```

**Step 3 - Test the configuration:**

**Ask Warp AI:**
```
"How do I manually start the Docker MCP gateway to see error messages?"
```

### Problem 3: Can't Connect to Router

**Error message:**

```
Error: Connection timed out
```

**Ask Warp AI:**
```
"My Juniper MCP server can't connect to my router with 'Connection timed out'. What should I check?"
```

**Warp AI will guide you through:**

1. **Test network connectivity:**
   ```bash
   ping 192.168.1.1
   ```

2. **Test SSH manually:**
   ```bash
   ssh admin@192.168.1.1
   ```

3. **Check firewall rules**

4. **Verify devices.json configuration**

### Problem 4: SSH Authentication Failed

**Error message:**

```
Error: Permission denied (publickey)
```

**Step 1 - Ask Warp AI:**

```
"SSH authentication is failing for my Juniper router. What are the most common causes?"
```

**Step 2 - Check key permissions:**

```bash
ls -l ~/network_devices/keys/id_rsa
```

Should show: `-rw-------` (600 permissions)

**If not, fix it:**
```bash
chmod 600 ~/network_devices/keys/id_rsa
```

**Step 3 - Verify key path in devices.json:**

```bash
cat ~/network_devices/devices.json
```

Make sure the path is: `/app/network_devices/keys/id_rsa` (not your local path!)

### Problem 5: Docker Out of Space

**Error message:**

```
Error: No space left on device
```

**Ask Warp AI:**
```
"Docker says 'no space left on device'. How do I clean up Docker images and containers?"
```

Warp AI will suggest:
```bash
# See disk usage
docker system df

# Clean up unused containers, networks, and images
docker system prune -a
```

### Problem 6: Warp Can't See MCP Servers

**Issue**: Warp AI doesn't recognize your MCP commands.

**Step 1 - Verify MCP is enabled in Warp:**

1. Open Warp Settings (`Cmd+,`)
2. Go to **Features**
3. Check **Model Context Protocol (MCP)** is enabled

**Step 2 - Check the configuration:**

**Ask Warp AI:**
```
"Show me my Warp MCP configuration"
```

Or manually check:
```bash
cat ~/.warp/mcp-config.json
```

**Step 3 - Restart Warp completely:**

- Quit Warp (`Cmd+Q`)
- Open Warp again

---

## Warp AI Prompt Library

Here's a collection of useful prompts organized by category. Save these for quick reference!

### Setup and Docker Prompts

```
"Show me all running Docker containers"

"How do I see Docker container logs for the MCP gateway?"

"What Docker images do I have installed?"

"How much disk space is Docker using?"

"How do I stop all Docker containers?"

"Restart the Docker MCP gateway container"
```

### Configuration Help Prompts

```
"Help me create a devices.json file for my Juniper router using SSH keys"

"What's the correct format for a jump host configuration in devices.json?"

"Check if my custom.yaml file has valid YAML syntax"

"Explain each field in the custom.yaml server definition"

"How do I add multiple routers to devices.json?"
```

### MCP Gateway Prompts

```
"List all MCP servers registered in my gateway"

"Show me what tools are available from the Juniper MCP server"

"How do I check if the MCP gateway is running?"

"Show me the configuration of my junos-network-manager server"

"What network tools are available besides Juniper?"
```

### Juniper Operations Prompts

```
"List all routers available in the MCP server"

"Show system health for my-router"

"Get the current configuration from my-router"

"Show interface status on my-router"

"Check BGP neighbors on my-router"

"Show OSPF neighbors on my-router"

"Display system logs from my-router"

"Get device facts and information for my-router"

"Compare current config with rollback 1 on my-router"
```

### Learning and Understanding Prompts

```
"Explain how the Docker MCP gateway works"

"What is the difference between a catalog and a registry in MCP?"

"Teach me basic Docker commands I should know"

"Explain Junos configuration hierarchy"

"What are the most important Junos show commands?"

"How does Junos rollback work?"
```

### Troubleshooting Prompts

```
"I got this error: [paste error]. What does it mean and how do I fix it?"

"Why can't Docker find my MCP server image?"

"My router SSH connection is failing. What should I check?"

"The MCP gateway is running but Warp can't connect. Help me debug this."

"How do I reset my MCP configuration and start fresh?"
```

### Safety and Best Practice Prompts

```
"Before I make this configuration change, what should I backup?"

"Review this Junos configuration command for errors: [paste command]"

"What's the safest way to test BGP changes?"

"How do I rollback a Junos configuration change?"

"What's the proper procedure for upgrading Junos software?"
```

---

## Best Practices and Security

### Security Considerations

#### 1. Protect Sensitive Files

**Never commit these files to version control:**
- `devices.json` (contains credentials)
- SSH private keys
- Any configuration files with passwords

**Ask Warp AI:**
```
"How do I check what files Git will commit before I commit them?"
```

#### 2. Use SSH Keys, Not Passwords

**Why**: SSH keys are much more secure.

**Generate a new SSH key:**

**Ask Warp AI:**
```
"How do I generate an SSH key pair for my Juniper routers?"
```

Warp AI will suggest:
```bash
ssh-keygen -t rsa -b 4096 -f ~/network_devices/keys/juniper_key
```

#### 3. Set Proper File Permissions

**Always secure your sensitive files:**

```bash
chmod 600 ~/network_devices/devices.json
chmod 600 ~/network_devices/keys/*
chmod 700 ~/.docker/mcp
```

**Ask Warp AI:**
```
"Why are 600 permissions important for SSH keys?"
```

#### 4. Review AI-Generated Configurations

**❌ Never do this:**
```
"Apply this BGP configuration to my router"
[Blindly accepting AI-generated config]
```

**✅ Always do this:**
```
"Generate a BGP configuration for this scenario"
[Review carefully]
[Ask: "Review this config for potential issues"]
[Test in lab]
[Then apply to production]
```

#### 5. Backup Before Changes

**Always backup before making configuration changes:**

```
"Get the full configuration from my-router and save it"
```

### Using the Gateway Effectively

#### 1. Organize Your Catalog Files

Keep your servers organized in `custom.yaml`:

```yaml
# Group by function
registry:
  # Network Infrastructure
  junos-network-manager:
    # config
  
  opnsense-firewall:
    # config
  
  # Virtualization
  proxmox-manager:
    # config
  
  # Security Tools
  kali-security:
    # config
```

#### 2. Use Descriptive Server Names

**Good names:**
- `junos-network-manager`
- `opnsense-firewall`
- `production-proxmox`

**Bad names:**
- `server1`
- `mcp`
- `test`

#### 3. Document Your Setup

Create a README in your network_devices folder:

**Ask Warp AI:**
```
"Create a template README file to document my MCP server setup"
```

#### 4. Keep Docker Images Updated

Regularly update your MCP server images:

```bash
# Pull latest images
docker pull docker/mcp-gateway
docker pull junos-mcp-server:latest

# Remove old images
docker image prune
```

#### 5. Monitor Docker Resource Usage

**Check regularly:**

```bash
docker system df
```

**Ask Warp AI:**
```
"My Docker is using a lot of disk space. What can I safely delete?"
```

### When to Use Warp AI vs Documentation

#### Use Warp AI for:
- ✅ Understanding unfamiliar commands quickly
- ✅ Troubleshooting errors
- ✅ Learning new concepts
- ✅ Generating basic configurations
- ✅ Explaining command output

#### Use Official Documentation for:
- ✅ Critical production changes
- ✅ Security-sensitive procedures
- ✅ Vendor-specific features
- ✅ Compliance requirements
- ✅ Final verification before applying configs

**Best practice**: Use Warp AI to learn and understand, then verify with official Juniper documentation for production changes.

---

## Warp Terminal Tips and Tricks

### Essential Keyboard Shortcuts

```
Ctrl+Shift+Space    - Open Warp AI
Ctrl+R              - Search command history
Ctrl+Shift+F        - Search in output
Cmd+K               - Clear screen
Cmd+T               - New tab
Cmd+D               - Split pane horizontally
Cmd+Shift+D         - Split pane vertically
Cmd+[number]        - Switch to tab number
```

### Organizing Your Warp Workspace

#### Use Tabs for Different Tasks

- **Tab 1**: MCP Gateway monitoring
- **Tab 2**: Juniper router operations
- **Tab 3**: Firewall management  
- **Tab 4**: Ad-hoc testing and troubleshooting

**Name your tabs:**
Right-click on tab → Rename Tab

#### Use Warp Workflows

Save frequently used command sequences as Workflows.

**Ask Warp AI:**
```
"How do I create a Warp Workflow for my daily router health checks?"
```

**Example Workflow**: "Daily Network Check"
```bash
# Check MCP gateway
docker ps | grep mcp-gateway

# List available routers
echo "Available routers"

# Check router health (you'll use MCP)
echo "Ask Warp AI: Show health status for all routers"
```

### Pro Tips for Network Engineers

#### Tip 1: Create Command Aliases

**Ask Warp AI:**
```
"How do I create command aliases in zsh?"
```

Example aliases:
```bash
# Add to ~/.zshrc
alias mcp-status='docker ps | grep mcp'
alias mcp-logs='docker logs $(docker ps -q --filter ancestor=docker/mcp-gateway)'
alias router-backup='echo "Use: Get full configuration from my-router"'
```

#### Tip 2: Save Common Docker Commands

Create a cheat sheet file:

```bash
nano ~/docker-mcp-cheatsheet.txt
```

Add:
```
# Docker MCP Cheat Sheet

# Check gateway status
docker ps | grep mcp-gateway

# View gateway logs
docker logs [container-id]

# Restart gateway
docker restart [container-id]

# Check disk usage
docker system df

# Clean up
docker system prune
```

#### Tip 3: Use Warp's AI for Learning

**Daily learning routine:**
```
"Teach me one advanced Junos command I should know"
"Explain a Docker networking concept"
"What's a useful feature of the MCP gateway I might not know about?"
```

#### Tip 4: Build Your Troubleshooting Playbook

Create `~/troubleshooting-playbook.md`:

```markdown
# Network Troubleshooting Playbook

## Router Won't Connect
1. Ping router: `ping [router-ip]`
2. Test SSH: `ssh admin@[router-ip]`
3. Check devices.json configuration
4. Verify SSH key permissions

## BGP Neighbor Down
1. Show BGP status: "Show BGP summary on my-router"
2. Check for route-maps: "Execute 'show route-filter' on my-router"
3. Verify neighbor IP reachability
4. Check firewall rules

## Interface Down
1. Show interface status
2. Check physical connectivity
3. Review interface errors
4. Check configuration
```

#### Tip 5: Leverage Warp's Command Blocks

Warp groups commands in blocks. You can:
- Click any block to see its full output
- Search within a block (`Ctrl+Shift+F`)
- Copy block output easily
- Collapse blocks to keep workspace clean

### Integration with Other Tools

#### Combine with Git for Configuration Management

**Ask Warp AI:**
```
"How do I create a Git repository to track my router configuration backups?"
```

#### Use with Notification Systems

**Ask Warp AI:**
```
"How can I get notified when my router health check finds an issue?"
```

#### Log to File for Records

```bash
# Create a daily log
echo "=== Network Health Check $(date) ===" >> ~/network-logs/daily-$(date +%Y-%m-%d).log
# Then use MCP to check routers
# Output gets saved to log
```

---

## Quick Reference Card

### Most Common Operations

| Task | How to Do It | Warp AI Help |
|------|--------------|--------------|
| List routers | "List all available routers" | "Show me router list command" |
| Check health | "Show system alarms for my-router" | "What indicates a healthy router?" |
| View config | "Get configuration from my-router" | "How do I save this config?" |
| Check interfaces | "Show interface status on my-router" | "Which interfaces should be up?" |
| Verify BGP | "Show BGP summary on my-router" | "What is normal BGP state?" |
| Compare configs | "Show config diff with rollback 1 for my-router" | "Explain this diff output" |
| Backup config | "Get configuration from my-router" → save to file | "Best way to backup configs?" |
| Check gateway | `docker ps | grep mcp-gateway` | "Is gateway running properly?" |

### Common Docker Commands

| Task | Command | What It Does |
|------|---------|--------------|
| List containers | `docker ps` | Show running containers |
| View logs | `docker logs [container-id]` | See container output |
| Stop container | `docker stop [container-id]` | Stop a container |
| Remove container | `docker rm [container-id]` | Delete a container |
| List images | `docker images` | Show downloaded images |
| Disk usage | `docker system df` | Check Docker disk space |
| Clean up | `docker system prune` | Remove unused containers/images |

### Common Warp AI Questions

```
"How do I [task]?"
"What does this error mean: [error]"
"Explain this output: [paste output]"
"Is this configuration safe: [paste config]"
"What's the best way to [task]?"
```

---

## Conclusion

Congratulations! You now know how to use the Docker MCP Gateway with Warp Terminal to manage your Juniper network devices.

### Key Takeaways

1. **Gateway Architecture**: One gateway manages all your MCP servers
2. **Warp AI**: Your 24/7 network assistant for commands and troubleshooting
3. **Catalog System**: Easy configuration through YAML files
4. **Scalable**: Start with Juniper, add firewalls and security tools later
5. **Beginner-Friendly**: Warp AI helps you learn as you go

### Next Steps

1. ✅ Set up your Docker MCP Gateway (if you haven't already)
2. ✅ Add your Juniper MCP server to the gateway
3. ✅ Configure Warp Terminal
4. ✅ Try the basic workflows with your routers
5. ✅ Explore adding other MCP servers (firewall, virtualization, security)

### Getting More Help

**Resources:**
- **Warp AI**: Press `Ctrl+Shift+Space` anytime
- **This Guide**: Bookmark for reference  
- **Juniper Documentation**: [juniper.net/documentation](https://www.juniper.net/documentation/)
- **Docker Documentation**: [docs.docker.com](https://docs.docker.com/)
- **MCP Protocol**: [Model Context Protocol docs](https://modelcontextprotocol.io/)

**Community:**
- Warp Discord
- Juniper Forums
- Docker Community Forums

---

**Happy Network Engineering with Warp AI and Docker MCP Gateway! 🚀**

*Remember: You don't need to be a programmer to use these tools effectively. The Docker MCP Gateway and Warp AI are designed to make your life easier, not harder!*

---

## Appendix: Real-World Scenarios

### Scenario 1: First Day with MCP Gateway

**Your goal**: Get comfortable with the basics.

**Step 1**: Check gateway is running
```bash
docker ps | grep mcp-gateway
```

**Step 2**: Ask Warp AI
```
"Show me all MCP servers registered in my gateway"
```

**Step 3**: Test Juniper connection
```
"List all available routers"
"Show device facts from my-router"
```

**Step 4**: Interpret results
```
"Explain what these device facts tell me about my router"
```

### Scenario 2: Troubleshooting a Network Issue

**Problem**: Users reporting slow network performance.

**Step 1**: Ask Warp AI for a plan
```
"Users report slow network. Give me a troubleshooting workflow using my Juniper router and MCP server"
```

**Step 2**: Follow Warp AI's suggestions
```
"Show interface statistics for my-router"
"Show chassis alarms on my-router"
"Execute 'show system buffers' on my-router"
```

**Step 3**: Analyze with Warp AI
```
"Review these interface statistics. Do I have a performance problem?"
```

### Scenario 3: Adding a New MCP Server

**Task**: Add OPNsense firewall management to your gateway.

**Step 1**: Build/pull the image
```bash
docker pull opnsense-mcp-server:latest
```

**Step 2**: Add to custom.yaml
```bash
nano ~/.docker/mcp/catalogs/custom.yaml
# Add server definition
```

**Step 3**: Update registry
```bash
nano ~/.docker/mcp/registry.yaml
# Add server name
```

**Step 4**: Restart Warp and test
```
"List all MCP servers"
"Show me tools available from OPNsense server"
```

### Scenario 4: Preparing for Maintenance

**Task**: Schedule maintenance window configuration change.

**Step 1**: Backup everything
```
"Get configuration from my-router"
```

**Step 2**: Save with timestamp
**Ask Warp AI:**
```
"How do I save this output to a file named with today's date?"
```

**Step 3**: Test changes in lab
```
"Generate a configuration for this change"
[Test in lab first]
```

**Step 4**: Document
```bash
# Create maintenance log
echo "Maintenance: $(date)" >> maintenance-log.txt
echo "Changes: [describe changes]" >> maintenance-log.txt
```

**Step 5**: Apply to production
```
"Load and commit this configuration to my-router: [paste config]"
```

**Step 6**: Verify
```
"Show configuration changes on my-router"
"Compare current config with backup"
```

---

**Version**: 2.0 (Docker MCP Gateway Edition)
**Last Updated**: 2025-01-16
**Maintained by**: Juniper MCP Server Community