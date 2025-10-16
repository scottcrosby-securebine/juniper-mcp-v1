# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Nilesh Simaria"
LABEL description="Junos MCP Server"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=30030
ENV MCP_TRANSPORT=stdio
ENV DEVICE_CONFIG=/app/network_devices/devices.json
ENV LOG_LEVEL=INFO
ENV FASTMCP_HOST=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    net-tools \
    iputils-ping \
    traceroute \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Create directories for configuration and logs
# Note: /app/network_devices is mounted from ${NETWORK_DEVICES_PATH} on the host
RUN mkdir -p /app/network_devices /app/logs /app/backups

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application and utils module
COPY jmcp.py .
COPY jmcp_token_manager.py .
COPY utils/ ./utils/

# Copy test files
COPY test_config_validation.py .
COPY test_invalid_devices.json .
COPY test_junos_cli.py .

# Copy configuration files
# COPY devices.json /app/config/devices.json

# Create a non-root user for security
RUN groupadd -r jmcp && useradd -r -g jmcp -s /bin/bash jmcp

# Set ownership and permissions
RUN chown -R jmcp:jmcp /app
RUN chmod +x jmcp.py

# Switch to non-root user
USER jmcp

# Expose the default port (though stdio transport doesn't need it)
EXPOSE 30030

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psutil; exit(0 if psutil.Process().is_running() else 1)"

# Default command
# /app/network_devices is mounted from ${NETWORK_DEVICES_PATH} on the host (via docker-compose or -v flag)
CMD ["python", "jmcp.py", "-f", "/app/network_devices/devices.json", "-t", "stdio"]
