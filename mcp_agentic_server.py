#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Agentic System

This module provides MCP protocol support for the Master Control Program,
allowing it to be used with MCP clients and the MCP inspector.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

# Set environment variables before importing anything
if not os.getenv('MCP_SECRET_KEY'):
    os.environ['MCP_SECRET_KEY'] = 'dev-secret-key-change-in-production'
if not os.getenv('MCP_DATABASE_URL'):
    os.environ['MCP_DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'

# Import MCP SDK
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_system.config import get_settings
from enhanced_code_agent import IntelligentCodeAgent

# Configure logging to go to stderr to avoid conflicts with MCP JSON-RPC protocol
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stderr  # Important: Use stderr to avoid stdout contamination
)
logger = logging.getLogger(__name__)


class MCPAgentServer:
    """MCP Server that exposes agentic capabilities."""
    
    def __init__(self):
        self.server = Server("mcp-agentic-server")
        self.settings = get_settings()
        self.code_agent = IntelligentCodeAgent()
        self._setup_capabilities()
    
    def _setup_capabilities(self):
        """Setup MCP server capabilities."""
        
        # List available tools
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="generate_code",
                    description="Generate code using AI agents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "language": {
                                "type": "string",
                                "description": "Programming language (python, javascript, etc.)",
                                "enum": ["python", "javascript", "typescript", "bash", "sql"]
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Code generation prompt"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for code generation",
                                "default": ""
                            }
                        },
                        "required": ["language", "prompt"]
                    }
                ),
                types.Tool(
                    name="analyze_code",
                    description="Analyze code for issues, patterns, and improvements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to analyze"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "enum": ["python", "javascript", "typescript", "bash", "sql"]
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis to perform",
                                "enum": ["quality", "security", "performance", "style", "all"],
                                "default": "all"
                            }
                        },
                        "required": ["code", "language"]
                    }
                ),
                types.Tool(
                    name="execute_code",
                    description="Execute code in a secure sandbox environment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to execute"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "enum": ["python", "javascript", "bash"]
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Execution timeout in seconds",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 300
                            }
                        },
                        "required": ["code", "language"]
                    }
                ),
                types.Tool(
                    name="create_task",
                    description="Create a new task for the agentic system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed task description"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Task priority",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium"
                            }
                        },
                        "required": ["title", "description"]
                    }
                ),
                types.Tool(
                    name="intelligent_code_analysis",
                    description="🎯 INTELLIGENT SOFTWARE AGENT: Simulate and debug source code like a senior engineer. Understands purpose, simulates behavior across states, identifies risks/bugs, and suggests meaningful improvements.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_name": {
                                "type": "string",
                                "description": "Class name, method name, or function name to analyze"
                            },
                            "method_name": {
                                "type": "string",
                                "description": "Optional: Specific method within a class to analyze",
                                "default": ""
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Optional: Specific file path to search in (relative to project root)",
                                "default": ""
                            },
                            "analysis_depth": {
                                "type": "string",
                                "description": "Depth of analysis to perform",
                                "enum": ["quick", "standard", "deep"],
                                "default": "standard"
                            }
                        },
                        "required": ["entity_name"]
                    }
                )
            ]
        
        # Call tool handler
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
            """Handle tool calls."""
            try:
                logger.info(f"MCP tool called: {name}", arguments=arguments)
                
                if name == "generate_code":
                    result = await self._generate_code(arguments)
                elif name == "analyze_code":
                    result = await self._analyze_code(arguments)
                elif name == "execute_code":
                    result = await self._execute_code(arguments)
                elif name == "create_task":
                    result = await self._create_task(arguments)
                elif name == "intelligent_code_analysis":
                    result = await self._intelligent_code_analysis(arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [types.TextContent(
                    type="text", 
                    text=json.dumps({"error": str(e)}, indent=2)
                )]
        
        # List available resources
        @self.server.list_resources()
        async def list_resources() -> List[types.Resource]:
            """List available resources."""
            return [
                types.Resource(
                    uri="mcp://agentic-server/status",
                    name="Server Status",
                    description="Current status of the agentic server",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="mcp://agentic-server/agents",
                    name="Active Agents",
                    description="List of currently active agents",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="mcp://agentic-server/metrics",
                    name="System Metrics",
                    description="Performance and usage metrics",
                    mimeType="application/json"
                )
            ]
        
        # Read resource handler
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content."""
            try:
                logger.info(f"MCP resource requested: {uri}")
                
                if uri == "mcp://agentic-server/status":
                    return json.dumps({
                        "status": "operational",
                        "version": "0.1.0",
                        "environment": self.settings.environment,
                        "features": ["code_generation", "code_analysis", "execution", "task_management"],
                        "health_checks": {
                            "api": "healthy",
                            "mcp_server": "healthy"
                        }
                    }, indent=2)
                
                elif uri == "mcp://agentic-server/agents":
                    return json.dumps({
                        "active_agents": [],
                        "available_types": [
                            "code_generation",
                            "code_analysis", 
                            "testing",
                            "security"
                        ],
                        "total_capacity": 10
                    }, indent=2)
                
                elif uri == "mcp://agentic-server/metrics":
                    return json.dumps({
                        "requests_total": 0,
                        "tools_called": 0,
                        "avg_response_time": 0.1,
                        "uptime_seconds": 0
                    }, indent=2)
                
                else:
                    raise ValueError(f"Unknown resource: {uri}")
                    
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
                raise
        
        # List available prompts
        @self.server.list_prompts()
        async def list_prompts() -> List[types.Prompt]:
            """List available prompts."""
            return [
                types.Prompt(
                    name="code-review",
                    description="Comprehensive code review prompt",
                    arguments=[
                        types.PromptArgument(
                            name="code",
                            description="Code to review",
                            required=True
                        ),
                        types.PromptArgument(
                            name="language",
                            description="Programming language",
                            required=True
                        )
                    ]
                ),
                types.Prompt(
                    name="debug-help",
                    description="Help debug code issues",
                    arguments=[
                        types.PromptArgument(
                            name="code",
                            description="Code with issues",
                            required=True
                        ),
                        types.PromptArgument(
                            name="error",
                            description="Error message",
                            required=True
                        )
                    ]
                )
            ]
        
        # Get prompt handler
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> types.GetPromptResult:
            """Get prompt content."""
            try:
                logger.info(f"MCP prompt requested: {name}", arguments=arguments)
                
                if name == "code-review":
                    code = arguments.get("code", "")
                    language = arguments.get("language", "")
                    
                    prompt = f"""Please perform a comprehensive code review for the following {language} code:

```{language}
{code}
```

Please provide feedback on:
1. Code quality and best practices
2. Potential bugs or issues  
3. Performance considerations
4. Security implications
5. Maintainability and readability
6. Specific suggestions for improvement"""

                elif name == "debug-help":
                    code = arguments.get("code", "")
                    error = arguments.get("error", "")
                    
                    prompt = f"""Help me debug this code issue:

Error: {error}

Code:
```
{code}
```

Please help me:
1. Identify the root cause
2. Explain why this error occurs
3. Provide step-by-step debugging approach
4. Suggest specific fixes with examples"""

                else:
                    raise ValueError(f"Unknown prompt: {name}")
                
                return types.GetPromptResult(
                    description=f"Generated prompt for {name}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=prompt)
                        )
                    ]
                )
                
            except Exception as e:
                logger.error(f"Error getting prompt {name}: {e}", exc_info=True)
                raise
    
    async def _generate_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using AI agents."""
        language = arguments.get("language")
        prompt = arguments.get("prompt")
        context = arguments.get("context", "")
        
        return {
            "status": "success",
            "language": language,
            "prompt": prompt,
            "generated_code": f"# Generated {language} code for: {prompt}\n# TODO: Implement actual code generation with agents",
            "explanation": "Code generation placeholder - would integrate with CodeGenerationAgent",
            "context_used": context
        }
    
    async def _analyze_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for issues and improvements."""
        code = arguments.get("code")
        language = arguments.get("language")
        analysis_type = arguments.get("analysis_type", "all")
        
        return {
            "status": "success",
            "language": language,
            "analysis_type": analysis_type,
            "issues": [
                {
                    "type": "style",
                    "severity": "info", 
                    "message": "Consider using more descriptive variable names",
                    "line": 1
                }
            ],
            "suggestions": [
                "This is a placeholder analysis result",
                "Would integrate with CodeAnalysisAgent for real analysis"
            ],
            "metrics": {
                "complexity": "low",
                "maintainability": "good",
                "lines_of_code": len(code.split('\n'))
            }
        }
    
    async def _execute_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code in sandbox environment."""
        code = arguments.get("code")
        language = arguments.get("language")
        timeout = arguments.get("timeout", 30)
        
        return {
            "status": "success",
            "language": language,
            "exit_code": 0,
            "stdout": "Code execution placeholder output\nWould integrate with ExecutionEngine for real execution",
            "stderr": "",
            "execution_time": 0.1,
            "timeout": timeout
        }
    
    async def _create_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task in the system."""
        title = arguments.get("title")
        description = arguments.get("description")
        priority = arguments.get("priority", "medium")
        
        return {
            "status": "success",
            "task_id": f"task_{hash(title) % 10000}",
            "title": title,
            "description": description,
            "priority": priority,
            "created_at": "2025-01-21T07:00:00Z",
            "status": "pending"
        }
    
    async def _intelligent_code_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 INTELLIGENT SOFTWARE AGENT
        
        Simulate and debug source code like a senior engineer would:
        1. Understand the purpose and intent of the class/method
        2. Simulate how it behaves across different states and inputs
        3. Debug the logic and identify risks or bugs
        4. Suggest meaningful improvements
        5. Think step-by-step and show execution behavior
        6. Ask clarification questions if logic is unclear
        """
        try:
            entity_name = arguments.get("entity_name")
            method_name = arguments.get("method_name") or None
            file_path = arguments.get("file_path") or None
            analysis_depth = arguments.get("analysis_depth", "standard")
            
            logger.info(f"🎯 Starting intelligent code analysis for '{entity_name}'", 
                       method_name=method_name, file_path=file_path, depth=analysis_depth)
            
            # Perform the comprehensive analysis
            analysis_result = self.code_agent.analyze_code_entity(
                entity_name=entity_name,
                method_name=method_name,
                file_path=file_path
            )
            
            # Enhance the result with agent-specific insights
            enhanced_result = {
                "🎯 INTELLIGENT AGENT ANALYSIS": "=== SENIOR ENGINEER CODE REVIEW ===",
                "agent_role": "Senior Software Engineer",
                "analysis_approach": "Systematic code simulation and debugging",
                "timestamp": analysis_result.get("analysis_timestamp"),
                
                "📍 CODE LOCATION": {
                    "entity": entity_name,
                    "method": method_name,
                    "file": analysis_result.get("file_location", "Not found"),
                    "confidence": f"{analysis_result.get('confidence_score', 0):.1f}%"
                },
                
                "🧠 PURPOSE & INTENT": analysis_result.get("purpose_analysis", {}),
                
                "⚡ BEHAVIOR SIMULATION": {
                    "description": "How this code behaves across different states and inputs",
                    "simulation_results": analysis_result.get("behavior_simulation", {}),
                    "step_by_step_execution": analysis_result.get("execution_flow", {})
                },
                
                "🐛 RISK & BUG ANALYSIS": {
                    "description": "Debugging the logic and identifying potential issues",
                    "findings": analysis_result.get("risk_analysis", {}),
                    "critical_issues": len(analysis_result.get("risk_analysis", {}).get("severity_levels", {}).get("critical", [])),
                    "high_priority_issues": len(analysis_result.get("risk_analysis", {}).get("severity_levels", {}).get("high", []))
                },
                
                "💡 MEANINGFUL IMPROVEMENTS": {
                    "description": "Actionable recommendations from a senior engineer perspective",
                    "suggestions": analysis_result.get("improvements", {}),
                    "justification": "Each suggestion is based on correctness, readability, and testability principles"
                },
                
                "❓ CLARIFICATION QUESTIONS": {
                    "description": "Questions to clarify unclear logic or assumptions",
                    "questions": analysis_result.get("clarification_questions", [])
                },
                
                "📊 TECH LEAD SUMMARY": {
                    "overall_assessment": self._generate_tech_lead_assessment(analysis_result),
                    "recommended_next_steps": self._get_prioritized_actions(analysis_result),
                    "team_impact": self._assess_team_impact(analysis_result)
                }
            }
            
            # Add error handling if analysis failed
            if "error" in analysis_result:
                enhanced_result["❌ ANALYSIS ERROR"] = {
                    "error": analysis_result["error"],
                    "debug_info": analysis_result.get("debug_info", {}),
                    "next_steps": [
                        "Check if the entity name is spelled correctly",
                        "Verify the file exists in the project directory",
                        "Try providing the file_path parameter",
                        "Check if the code is syntactically valid"
                    ]
                }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in intelligent code analysis: {e}", exc_info=True)
            return {
                "❌ ANALYSIS FAILED": str(e),
                "error_type": type(e).__name__,
                "senior_engineer_advice": [
                    "This error suggests the analysis engine encountered an unexpected issue",
                    "Check the entity name and file path for correctness",
                    "Ensure the code is syntactically valid Python",
                    "Try with a simpler entity first to verify the system is working"
                ]
            }
    
    def _generate_tech_lead_assessment(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a tech lead style assessment of the code."""
        confidence = analysis_result.get("confidence_score", 0)
        critical_issues = len(analysis_result.get("risk_analysis", {}).get("severity_levels", {}).get("critical", []))
        high_issues = len(analysis_result.get("risk_analysis", {}).get("severity_levels", {}).get("high", []))
        
        if critical_issues > 0:
            return f"🚨 CRITICAL: {critical_issues} critical issues found. Immediate attention required before production."
        elif high_issues > 2:
            return f"⚠️ HIGH RISK: {high_issues} high-priority issues. Recommend addressing before next release."
        elif confidence < 70:
            return "🔍 NEEDS INVESTIGATION: Analysis confidence is low. More context or documentation needed."
        else:
            return "✅ GOOD: Code appears well-structured. Focus on the suggested improvements for optimization."
    
    def _get_prioritized_actions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get prioritized actions from the improvements."""
        improvements = analysis_result.get("improvements", {})
        prioritized = improvements.get("prioritized_actions", [])
        
        if prioritized:
            return [action.get("improvement", "Unknown action") for action in prioritized[:3]]
        else:
            return [
                "Review the code structure and naming conventions",
                "Add comprehensive unit tests",
                "Improve documentation and type hints"
            ]
    
    def _assess_team_impact(self, analysis_result: Dict[str, Any]) -> str:
        """Assess the impact on the team."""
        risk_analysis = analysis_result.get("risk_analysis", {})
        maintainability_issues = len(risk_analysis.get("maintainability_issues", []))
        
        if maintainability_issues > 3:
            return "HIGH: Multiple maintainability issues may slow down team development"
        elif maintainability_issues > 1:
            return "MEDIUM: Some maintainability concerns that could affect team velocity"
        else:
            return "LOW: Code is generally maintainable and shouldn't block team progress"
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting MCP agentic server")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for MCP server."""
    server = MCPAgentServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 