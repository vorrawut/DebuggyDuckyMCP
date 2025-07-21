# MCP Inspector Usage Guide

This guide explains how to use the `@modelcontextprotocol/inspector` with your MCP (Master Control Program) agentic server.

## 🎯 Overview

Your agentic server now supports the **Model Context Protocol (MCP)**, which means you can:
- ✅ Use the MCP Inspector to debug and explore capabilities
- ✅ Connect to MCP-compatible AI assistants and applications  
- ✅ Expose your agentic tools, resources, and prompts via MCP protocol

## 🚀 Quick Start

### Method 1: Using MCP Inspector Directly

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run the inspector with your MCP server
npx @modelcontextprotocol/inspector python mcp_agentic_server.py
```

### Method 2: Using Configuration File

```bash
# Run the inspector with the configuration file
npx @modelcontextprotocol/inspector --config mcp.json
```

### Method 3: Alternative Script (if needed)

```bash
# Use the wrapper script
npx @modelcontextprotocol/inspector python run_mcp_server.py
```

## 📋 Available Capabilities

Your MCP server exposes the following capabilities:

### 🛠️ Tools (Functions)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `generate_code` | Generate code using AI agents | `language`, `prompt`, `context` |
| `analyze_code` | Analyze code for issues and improvements | `code`, `language`, `analysis_type` |
| `execute_code` | Execute code in secure sandbox | `code`, `language`, `timeout` |
| `create_task` | Create new task for agentic system | `title`, `description`, `priority` |

### 📊 Resources (Data)

| Resource URI | Description |
|--------------|-------------|
| `mcp://agentic-server/status` | Current server status and health |
| `mcp://agentic-server/agents` | Active agents information |
| `mcp://agentic-server/metrics` | Performance and usage metrics |

### 💬 Prompts (Templates)

| Prompt Name | Description | Arguments |
|-------------|-------------|-----------|
| `code-review` | Comprehensive code review prompt | `code`, `language` |
| `debug-help` | Help debug code issues | `code`, `error` |

## 🔧 Usage Examples

### Example 1: Generate Python Code

In the MCP Inspector, call the `generate_code` tool:

```json
{
  "language": "python",
  "prompt": "Create a function to calculate fibonacci numbers",
  "context": "Need an efficient implementation for large numbers"
}
```

### Example 2: Analyze Code Quality

Call the `analyze_code` tool:

```json
{
  "code": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
  "language": "python",
  "analysis_type": "performance"
}
```

### Example 3: Execute Code Safely

Call the `execute_code` tool:

```json
{
  "code": "print('Hello from MCP!')\nfor i in range(3):\n    print(f'Count: {i}')",
  "language": "python",
  "timeout": 10
}
```

### Example 4: Read Server Status

Access the `mcp://agentic-server/status` resource to see:

```json
{
  "status": "operational",
  "version": "0.1.0",
  "environment": "development",
  "features": ["code_generation", "code_analysis", "execution", "task_management"],
  "health_checks": {
    "api": "healthy",
    "mcp_server": "healthy"
  }
}
```

### Example 5: Use Code Review Prompt

Call the `code-review` prompt:

```json
{
  "code": "class Calculator:\n    def add(self, a, b):\n        return a + b",
  "language": "python"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot import name 'types' from 'mcp'"**
   - This indicates a naming conflict
   - Solution: The package has been renamed to `mcp_system` to avoid conflicts

2. **"MCP_SECRET_KEY is required"**
   - Environment variables are missing
   - Solution: Environment variables are automatically set in the scripts

3. **"Server not responding"**
   - Check if the virtual environment is activated
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Debugging Steps

1. **Test MCP server directly:**
   ```bash
   source venv/bin/activate
   python mcp_agentic_server.py
   ```
   (Should show "Starting MCP agentic server" and wait for input)

2. **Check dependencies:**
   ```bash
   source venv/bin/activate
   pip list | grep mcp
   ```
   (Should show `mcp` package installed)

3. **Verify configuration:**
   ```bash
   cat mcp.json
   ```
   (Should show valid JSON configuration)

## 🌟 Advanced Usage

### Custom Environment Variables

You can customize the server behavior by setting environment variables:

```bash
export MCP_ENVIRONMENT=development
export MCP_LOG_LEVEL=DEBUG
export MCP_SECRET_KEY="your-secret-key"
export MCP_DATABASE_URL="your-database-url"

npx @modelcontextprotocol/inspector python mcp_agentic_server.py
```

### Integration with AI Assistants

Your MCP server can be integrated with AI assistants that support MCP:

1. **Claude Desktop**: Add to your configuration file
2. **VS Code Extensions**: Use MCP-compatible extensions
3. **Custom Applications**: Use the MCP SDK to connect

### Extending Capabilities

To add new tools, resources, or prompts:

1. Edit `mcp_agentic_server.py`
2. Add new tool definitions in `_setup_capabilities()`
3. Implement the corresponding handler methods
4. Test with the MCP Inspector

## 📚 Next Steps

1. **Integrate with Real Agents**: Replace placeholder implementations with actual agent calls
2. **Add Authentication**: Implement secure access controls
3. **Expand Tools**: Add more specialized tools for your use cases
4. **Monitor Usage**: Add metrics and logging for production use

## 🔗 Useful Links

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 💡 Tips

- Use the inspector's built-in testing features to validate your tools
- Check the logs in your terminal for debugging information
- The inspector provides schema validation for your tools and resources
- You can use the inspector to generate client code for other applications 