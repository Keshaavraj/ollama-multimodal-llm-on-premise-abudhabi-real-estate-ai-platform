# MCP Server Dockerfile – Real Estate Live Data
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server
COPY server.py .

# Expose MCP HTTP port
EXPOSE 8080

# Run as HTTP server inside Docker (stdio is used for Claude Desktop only)
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8080

# Health check hits the /mcp endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/mcp || exit 1

CMD ["python3", "server.py"]
