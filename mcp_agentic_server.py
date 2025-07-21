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
from pathlib import Path
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
                ),
                types.Tool(
                    name="line_level_code_analysis",
                    description="🔍 LINE-LEVEL INTELLIGENT AGENT: Senior engineer + dynamic code simulator. Analyzes specific lines, variables, or methods from local files. Perfect for debugging, validation, and targeted improvements.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Absolute or relative file path (e.g., /Users/vorrawutjudasri/project/src/main/kotlin/Config.kt)"
                            },
                            "line_number": {
                                "type": "string",
                                "description": "Target line number or range (e.g., '42' or '42-45')"
                            },
                            "target_symbol": {
                                "type": "string",
                                "description": "Optional: Specific variable, method, or symbol to focus on",
                                "default": ""
                            },
                            "question": {
                                "type": "string",
                                "description": "Your specific question about the code (e.g., 'Why is this variable possibly null?')"
                            },
                            "context_lines": {
                                "type": "integer",
                                "description": "Number of context lines before/after target (default: 20)",
                                "default": 20,
                                "minimum": 5,
                                "maximum": 100
                            },
                            "project_type": {
                                "type": "string",
                                "description": "Project type for better context understanding",
                                "enum": ["spring_boot", "kotlin", "java", "python", "javascript", "typescript", "auto_detect"],
                                "default": "auto_detect"
                            }
                        },
                        "required": ["file_path", "line_number", "question"]
                    }
                )
            ]
        
        # Call tool handler
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
            """Handle tool calls."""
            try:
                logger.info(f"MCP tool called: {name} with arguments: {arguments}")
                
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
                elif name == "line_level_code_analysis":
                    result = await self._line_level_code_analysis(arguments)
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
                logger.info(f"MCP prompt requested: {name} with arguments: {arguments}")
                
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
            
            logger.info(f"🎯 Starting intelligent code analysis for '{entity_name}' (method={method_name}, file={file_path}, depth={analysis_depth})")
            
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
    
    async def _line_level_code_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 LINE-LEVEL INTELLIGENT AGENT
        
        Acts as a senior software engineer + dynamic code simulator.
        Analyzes specific lines, variables, or methods from local files.
        Perfect for debugging, validation, and targeted improvements.
        """
        try:
            file_path = arguments.get("file_path")
            line_number = arguments.get("line_number")
            target_symbol = arguments.get("target_symbol", "")
            question = arguments.get("question")
            context_lines = arguments.get("context_lines", 20)
            project_type = arguments.get("project_type", "auto_detect")
            
            logger.info(f"🔍 Line-level analysis for {file_path}:{line_number} (symbol={target_symbol})")
            
            # Resolve file path (absolute or relative)
            file_path_obj = Path(file_path)
            if not file_path_obj.is_absolute():
                # Try relative to current working directory
                file_path_obj = Path.cwd() / file_path
                
            if not file_path_obj.exists():
                return {
                    "❌ FILE NOT FOUND": f"Could not locate file: {file_path}",
                    "attempted_paths": [str(file_path_obj)],
                    "suggestions": [
                        "Check if the file path is correct",
                        "Ensure the file exists on your machine",
                        "Try using an absolute path",
                        "Verify file permissions"
                    ]
                }
            
            # Parse line number (single or range)
            try:
                if '-' in line_number:
                    start_line, end_line = map(int, line_number.split('-'))
                else:
                    start_line = end_line = int(line_number)
            except ValueError:
                return {
                    "❌ INVALID LINE NUMBER": f"Could not parse line number: {line_number}",
                    "expected_format": "Single line (e.g., '42') or range (e.g., '42-45')"
                }
            
            # Read file content
            try:
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                return {
                    "❌ FILE READ ERROR": f"Could not read file: {e}",
                    "file_path": str(file_path_obj)
                }
            
            total_lines = len(lines)
            
            # Validate line numbers
            if start_line < 1 or start_line > total_lines:
                return {
                    "❌ LINE OUT OF RANGE": f"Line {start_line} is out of range (file has {total_lines} lines)",
                    "valid_range": f"1-{total_lines}"
                }
            
            # Extract target lines and context
            context_start = max(1, start_line - context_lines)
            context_end = min(total_lines, end_line + context_lines)
            
            target_lines = []
            context_before = []
            context_after = []
            
            for i, line in enumerate(lines, 1):
                if context_start <= i < start_line:
                    context_before.append(f"{i:4d}: {line.rstrip()}")
                elif start_line <= i <= end_line:
                    target_lines.append(f"{i:4d}: {line.rstrip()}")
                elif end_line < i <= context_end:
                    context_after.append(f"{i:4d}: {line.rstrip()}")
            
            # Auto-detect project type if needed
            if project_type == "auto_detect":
                project_type = self._detect_project_type(file_path_obj, lines)
            
            # Perform line-level analysis
            analysis = self._analyze_target_lines(
                target_lines=target_lines,
                context_before=context_before,
                context_after=context_after,
                target_symbol=target_symbol,
                question=question,
                project_type=project_type,
                file_path=str(file_path_obj)
            )
            
            return {
                "🔍 LINE-LEVEL INTELLIGENT ANALYSIS": "=== SENIOR ENGINEER + CODE SIMULATOR ===",
                "agent_role": "Senior Software Engineer & Dynamic Code Simulator",
                "analysis_target": f"{file_path}:{line_number}",
                
                "📍 LOCATION CONTEXT": {
                    "file_path": str(file_path_obj),
                    "target_lines": f"{start_line}-{end_line}",
                    "total_file_lines": total_lines,
                    "context_range": f"{context_start}-{context_end}",
                    "project_type": project_type,
                    "target_symbol": target_symbol or "None specified"
                },
                
                "❓ YOUR QUESTION": question,
                
                "📝 CODE CONTEXT": {
                    "lines_before": context_before[-10:] if len(context_before) > 10 else context_before,
                    "target_lines": target_lines,
                    "lines_after": context_after[:10] if len(context_after) > 10 else context_after
                },
                
                "🧠 SENIOR ENGINEER ANALYSIS": analysis.get("engineer_analysis", {}),
                "⚡ RUNTIME SIMULATION": analysis.get("runtime_simulation", {}),
                "🐛 RISK ASSESSMENT": analysis.get("risk_assessment", {}),
                "💡 TARGETED IMPROVEMENTS": analysis.get("improvements", {}),
                "🔧 DEBUGGING INSIGHTS": analysis.get("debugging_insights", {}),
                
                "📊 ENGINEER'S VERDICT": analysis.get("verdict", "Analysis complete")
            }
            
        except Exception as e:
            logger.error(f"Error in line-level analysis: {e}", exc_info=True)
            return {
                "❌ ANALYSIS FAILED": str(e),
                "error_type": type(e).__name__,
                "debug_info": {
                    "file_path": file_path,
                    "line_number": line_number,
                    "target_symbol": target_symbol
                },
                "senior_engineer_advice": [
                    "This error suggests an issue with file access or parsing",
                    "Check if the file path is accessible and readable",
                    "Ensure the line number format is correct",
                    "Try with a simpler file first to verify the system"
                ]
            }
    
    def _detect_project_type(self, file_path: Path, lines: list) -> str:
        """Auto-detect project type based on file extension and content."""
        file_ext = file_path.suffix.lower()
        content = ''.join(lines[:50])  # Check first 50 lines
        
        if file_ext == '.kt':
            if 'import org.springframework' in content:
                return "spring_boot"
            return "kotlin"
        elif file_ext == '.java':
            if 'import org.springframework' in content or '@SpringBootApplication' in content:
                return "spring_boot"
            return "java"
        elif file_ext == '.py':
            if 'from fastapi' in content or 'import fastapi' in content:
                return "fastapi"
            elif 'from django' in content or 'import django' in content:
                return "django"
            return "python"
        elif file_ext in ['.js', '.jsx']:
            if 'import React' in content or 'from "react"' in content:
                return "react"
            return "javascript"
        elif file_ext in ['.ts', '.tsx']:
            if 'import React' in content:
                return "react_typescript"
            return "typescript"
        else:
            return "unknown"
    
    def _analyze_target_lines(self, target_lines: list, context_before: list, 
                            context_after: list, target_symbol: str, question: str,
                            project_type: str, file_path: str) -> Dict[str, Any]:
        """Perform detailed line-level analysis like a senior engineer."""
        
        target_code = '\n'.join([line.split(':', 1)[1].strip() if ':' in line else line for line in target_lines])
        context_code = '\n'.join([line.split(':', 1)[1].strip() if ':' in line else line for line in context_before + target_lines + context_after])
        
        analysis = {
            "engineer_analysis": {},
            "runtime_simulation": {},
            "risk_assessment": {},
            "improvements": {},
            "debugging_insights": {},
            "verdict": ""
        }
        
        # 1. Engineering Analysis
        analysis["engineer_analysis"] = {
            "code_purpose": self._analyze_code_purpose(target_code, context_code, project_type),
            "variable_analysis": self._analyze_variables(target_code, target_symbol),
            "method_context": self._analyze_method_context(context_code),
            "dependencies": self._analyze_dependencies(context_code, project_type),
            "patterns_detected": self._detect_code_patterns(target_code, project_type)
        }
        
        # 2. Runtime Simulation
        analysis["runtime_simulation"] = {
            "execution_flow": self._simulate_execution_flow(target_code, context_code),
            "variable_states": self._simulate_variable_states(target_code, target_symbol),
            "lifecycle_analysis": self._analyze_lifecycle(context_code, project_type),
            "error_scenarios": self._simulate_error_scenarios(target_code)
        }
        
        # 3. Risk Assessment
        analysis["risk_assessment"] = {
            "null_safety": self._analyze_null_safety(target_code, project_type),
            "concurrency_risks": self._analyze_concurrency_risks(target_code, context_code),
            "performance_concerns": self._analyze_performance_concerns(target_code),
            "security_implications": self._analyze_security_implications(target_code)
        }
        
        # 4. Targeted Improvements
        analysis["improvements"] = {
            "immediate_fixes": self._suggest_immediate_fixes(target_code, question),
            "robustness_improvements": self._suggest_robustness_improvements(target_code, project_type),
            "code_quality": self._suggest_code_quality_improvements(target_code),
            "best_practices": self._suggest_best_practices(target_code, project_type)
        }
        
        # 5. Debugging Insights
        analysis["debugging_insights"] = {
            "common_issues": self._identify_common_issues(target_code, project_type),
            "debugging_approach": self._suggest_debugging_approach(target_code, question),
            "test_scenarios": self._suggest_test_scenarios(target_code),
            "monitoring_points": self._suggest_monitoring_points(target_code)
        }
        
        # 6. Engineer's Verdict
        analysis["verdict"] = self._generate_engineer_verdict(target_code, question, analysis)
        
        return analysis
    
    def _analyze_code_purpose(self, target_code: str, context_code: str, project_type: str) -> str:
        """Analyze the purpose of the target code."""
        if 'fun ' in target_code or 'def ' in target_code:
            return "Function/method definition"
        elif '=' in target_code and ('val ' in target_code or 'var ' in target_code):
            return "Variable declaration/assignment"
        elif '@' in target_code:
            return "Annotation or decorator"
        elif 'class ' in target_code:
            return "Class definition"
        elif 'import ' in target_code:
            return "Import statement"
        elif 'if ' in target_code or 'when ' in target_code:
            return "Conditional logic"
        elif 'for ' in target_code or 'while ' in target_code:
            return "Loop construct"
        else:
            return "Statement or expression"
    
    def _analyze_variables(self, target_code: str, target_symbol: str) -> Dict[str, Any]:
        """Analyze variables in the target code."""
        variables = {
            "declared_variables": [],
            "used_variables": [],
            "target_symbol_analysis": {},
            "type_inferences": {}
        }
        
        # Basic variable detection
        import re
        
        # Kotlin/Java variable declarations
        kotlin_vars = re.findall(r'(val|var)\s+(\w+)', target_code)
        variables["declared_variables"].extend([var[1] for var in kotlin_vars])
        
        # Python variable assignments
        python_vars = re.findall(r'(\w+)\s*=', target_code)
        variables["declared_variables"].extend(python_vars)
        
        if target_symbol:
            variables["target_symbol_analysis"] = {
                "symbol": target_symbol,
                "present_in_code": target_symbol in target_code,
                "usage_count": target_code.count(target_symbol),
                "context": "Analyzing symbol usage patterns"
            }
        
        return variables
    
    def _analyze_method_context(self, context_code: str) -> Dict[str, Any]:
        """Analyze the method/function context."""
        context = {
            "enclosing_method": "Unknown",
            "enclosing_class": "Unknown",
            "access_level": "Unknown",
            "parameters": [],
            "return_type": "Unknown"
        }
        
        # Basic method detection
        if 'fun ' in context_code:
            context["enclosing_method"] = "Kotlin function detected"
        elif 'def ' in context_code:
            context["enclosing_method"] = "Python function detected"
        elif 'public ' in context_code or 'private ' in context_code:
            context["access_level"] = "Java/Kotlin method detected"
        
        return context
    
    def _analyze_dependencies(self, context_code: str, project_type: str) -> list:
        """Analyze dependencies and imports."""
        dependencies = []
        
        if project_type == "spring_boot":
            if '@Autowired' in context_code:
                dependencies.append("Spring dependency injection detected")
            if '@Bean' in context_code:
                dependencies.append("Spring bean configuration")
            if '@Service' in context_code or '@Component' in context_code:
                dependencies.append("Spring stereotype annotation")
        
        return dependencies
    
    def _detect_code_patterns(self, target_code: str, project_type: str) -> list:
        """Detect code patterns and idioms."""
        patterns = []
        
        if '?.' in target_code:
            patterns.append("Safe call operator (null-safe)")
        if '!!' in target_code:
            patterns.append("Not-null assertion operator (potentially unsafe)")
        if 'try {' in target_code or 'try:' in target_code:
            patterns.append("Exception handling")
        if 'lazy' in target_code:
            patterns.append("Lazy initialization")
        
        return patterns
    
    def _simulate_execution_flow(self, target_code: str, context_code: str) -> Dict[str, Any]:
        """Simulate how the code would execute."""
        return {
            "execution_order": "Sequential unless control flow changes",
            "potential_branches": "Conditional execution detected" if 'if' in target_code else "Linear execution",
            "side_effects": "Possible state changes" if '=' in target_code else "Read-only operations"
        }
    
    def _simulate_variable_states(self, target_code: str, target_symbol: str) -> Dict[str, Any]:
        """Simulate variable state changes."""
        if target_symbol:
            return {
                "initial_state": "Unknown",
                "after_execution": "Potentially modified" if target_symbol in target_code and '=' in target_code else "Unchanged",
                "nullability": "Check null safety patterns"
            }
        return {"note": "No target symbol specified"}
    
    def _analyze_lifecycle(self, context_code: str, project_type: str) -> str:
        """Analyze component lifecycle."""
        if project_type == "spring_boot":
            if '@PostConstruct' in context_code:
                return "Spring bean initialization phase"
            elif '@PreDestroy' in context_code:
                return "Spring bean destruction phase"
        return "Standard object lifecycle"
    
    def _simulate_error_scenarios(self, target_code: str) -> list:
        """Simulate potential error scenarios."""
        scenarios = []
        
        if '!!' in target_code:
            scenarios.append("KotlinNullPointerException if value is null")
        if '[' in target_code:
            scenarios.append("IndexOutOfBoundsException possible")
        if '/' in target_code:
            scenarios.append("ArithmeticException (division by zero)")
        
        return scenarios
    
    def _analyze_null_safety(self, target_code: str, project_type: str) -> Dict[str, Any]:
        """Analyze null safety aspects."""
        analysis = {
            "null_safety_level": "Unknown",
            "risky_operations": [],
            "safe_operations": []
        }
        
        if project_type == "kotlin":
            if '!!' in target_code:
                analysis["risky_operations"].append("Not-null assertion (!!) - can throw NPE")
            if '?.' in target_code:
                analysis["safe_operations"].append("Safe call operator (?.) - null-safe")
            if '?' in target_code and 'fun' in target_code:
                analysis["null_safety_level"] = "Nullable types properly declared"
        
        return analysis
    
    def _analyze_concurrency_risks(self, target_code: str, context_code: str) -> list:
        """Analyze concurrency-related risks."""
        risks = []
        
        if 'var ' in target_code and '@' in context_code:
            risks.append("Mutable variable in potentially shared context")
        if 'synchronized' in target_code or 'lock' in target_code:
            risks.append("Explicit synchronization detected")
        
        return risks
    
    def _analyze_performance_concerns(self, target_code: str) -> list:
        """Analyze performance implications."""
        concerns = []
        
        if 'for' in target_code and 'for' in target_code:
            concerns.append("Nested loops detected - O(n²) complexity")
        if 'lazy' in target_code:
            concerns.append("Lazy initialization - first access cost")
        
        return concerns
    
    def _analyze_security_implications(self, target_code: str) -> list:
        """Analyze security implications."""
        implications = []
        
        if 'password' in target_code.lower():
            implications.append("Password handling detected - ensure proper security")
        if 'sql' in target_code.lower():
            implications.append("SQL operations - check for injection vulnerabilities")
        
        return implications
    
    def _suggest_immediate_fixes(self, target_code: str, question: str) -> list:
        """Suggest immediate fixes based on the question."""
        fixes = []
        
        if 'null' in question.lower():
            if '!!' in target_code:
                fixes.append("Replace !! with safe call ?. or add null check")
        if 'robust' in question.lower():
            fixes.append("Add error handling with try-catch")
            fixes.append("Add input validation")
        
        return fixes
    
    def _suggest_robustness_improvements(self, target_code: str, project_type: str) -> list:
        """Suggest robustness improvements."""
        improvements = []
        
        if project_type == "spring_boot":
            improvements.append("Add @Validated annotation for input validation")
            improvements.append("Consider circuit breaker pattern for external calls")
        
        improvements.append("Add comprehensive error handling")
        improvements.append("Include logging for debugging")
        
        return improvements
    
    def _suggest_code_quality_improvements(self, target_code: str) -> list:
        """Suggest code quality improvements."""
        return [
            "Add meaningful variable names",
            "Include documentation/comments",
            "Consider extracting complex logic to methods",
            "Add unit tests for this code"
        ]
    
    def _suggest_best_practices(self, target_code: str, project_type: str) -> list:
        """Suggest best practices specific to the project type."""
        practices = []
        
        if project_type == "kotlin":
            practices.append("Use data classes for value objects")
            practices.append("Prefer val over var when possible")
            practices.append("Use sealed classes for restricted hierarchies")
        elif project_type == "spring_boot":
            practices.append("Use constructor injection over field injection")
            practices.append("Make beans immutable when possible")
            practices.append("Use @ConfigurationProperties for configuration")
        
        return practices
    
    def _identify_common_issues(self, target_code: str, project_type: str) -> list:
        """Identify common issues for this type of code."""
        issues = []
        
        if '!!' in target_code:
            issues.append("Not-null assertion can cause runtime crashes")
        if 'var ' in target_code:
            issues.append("Mutable variables can lead to unexpected state changes")
        
        return issues
    
    def _suggest_debugging_approach(self, target_code: str, question: str) -> list:
        """Suggest debugging approach."""
        approaches = []
        
        if 'null' in question.lower():
            approaches.append("Add null checks and logging before the problematic line")
            approaches.append("Use debugger to inspect variable states")
        
        approaches.append("Add strategic log statements")
        approaches.append("Write unit tests to isolate the issue")
        approaches.append("Use IDE debugger with breakpoints")
        
        return approaches
    
    def _suggest_test_scenarios(self, target_code: str) -> list:
        """Suggest test scenarios."""
        return [
            "Test with valid input values",
            "Test with null/empty values",
            "Test with boundary conditions",
            "Test error handling paths"
        ]
    
    def _suggest_monitoring_points(self, target_code: str) -> list:
        """Suggest monitoring points."""
        return [
            "Add metrics for execution time",
            "Monitor error rates",
            "Track method call frequency",
            "Alert on unexpected null values"
        ]
    
    def _generate_engineer_verdict(self, target_code: str, question: str, analysis: Dict[str, Any]) -> str:
        """Generate final engineer verdict."""
        risks = analysis.get("risk_assessment", {})
        null_risks = len(risks.get("null_safety", {}).get("risky_operations", []))
        
        if null_risks > 0:
            return f"⚠️ ATTENTION NEEDED: {null_risks} null safety risks detected. Address before production."
        elif '!!' in target_code:
            return "🚨 RISKY CODE: Not-null assertions present. Consider safer alternatives."
        else:
            return "✅ CODE REVIEW: Generally safe. Follow suggested improvements for robustness."
    
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