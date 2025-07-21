#!/usr/bin/env python3
"""
MCP Server Standalone Runner

This script runs the MCP (Model Context Protocol) server for the 
Master Control Program agentic system.

Usage:
    python run_mcp_server.py

For use with MCP Inspector:
    npx @modelcontextprotocol/inspector python run_mcp_server.py
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variables if not set
if not os.getenv('MCP_SECRET_KEY'):
    os.environ['MCP_SECRET_KEY'] = 'dev-secret-key-change-in-production'
if not os.getenv('MCP_DATABASE_URL'):
    os.environ['MCP_DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'

from mcp_agentic_server import main

if __name__ == "__main__":
    asyncio.run(main()) 