#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set required environment variables
export MCP_SECRET_KEY="dev-secret-key-change-in-production"
export MCP_DATABASE_URL="postgresql://test:test@localhost:5432/test"

# Start the server
echo "🚀 Starting MCP server..."
python main.py 