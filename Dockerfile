# Multi-stage Dockerfile for MCP Application

# ============================================================================
# Base Stage - Common dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Development Stage
# ============================================================================
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest-xvfb \
    ipython \
    jupyter \
    debugpy

# Install Docker CLI for Docker-in-Docker execution
RUN curl -fsSL https://get.docker.com | sh

# Copy application code
COPY . .

# Change ownership to mcp user
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Expose port
EXPOSE 8000

# Development command (overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Production Stage
# ============================================================================
FROM base as production

# Copy application code
COPY . .

# Install the application
RUN pip install --no-cache-dir -e .

# Change ownership to mcp user
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ============================================================================
# Testing Stage
# ============================================================================
FROM base as testing

# Install test dependencies
RUN pip install --no-cache-dir pytest-cov pytest-asyncio

# Copy application code
COPY . .

# Change ownership to mcp user
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Run tests
CMD ["pytest", "--cov=mcp", "--cov-report=term-missing", "--cov-report=html"] 