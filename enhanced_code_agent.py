#!/usr/bin/env python3
"""
Intelligent Software Agent for Code Analysis

This module implements an intelligent software agent that operates within the MCP 
system to simulate and debug source code like a senior engineer would.
"""

import ast
import inspect
import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import re


class IntelligentCodeAgent:
    """
    Intelligent software agent for code simulation and debugging.
    Acts like a senior engineer analyzing code behavior, risks, and improvements.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.loaded_modules = {}
        self.analysis_cache = {}
    
    def analyze_code_entity(self, 
                           entity_name: str, 
                           method_name: Optional[str] = None,
                           file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for code analysis.
        
        Args:
            entity_name: Class name, function name, or module name
            method_name: Optional specific method to analyze
            file_path: Optional specific file path to search in
            
        Returns:
            Comprehensive analysis report
        """
        try:
            # Step 1: Load context and find the entity
            context = self._load_context(entity_name, method_name, file_path)
            
            if not context:
                return {
                    "error": f"Could not find entity '{entity_name}' in the codebase",
                    "suggestions": [
                        "Check if the class/method name is spelled correctly",
                        "Ensure the file is in the project directory",
                        "Try providing the file_path parameter"
                    ]
                }
            
            # Step 2: Understand purpose and intent
            purpose_analysis = self._analyze_purpose(context)
            
            # Step 3: Simulate behavior across different states
            behavior_simulation = self._simulate_behavior(context)
            
            # Step 4: Debug logic and identify risks
            risk_analysis = self._identify_risks_and_bugs(context)
            
            # Step 5: Suggest meaningful improvements
            improvements = self._suggest_improvements(context, risk_analysis)
            
            # Step 6: Generate execution flow analysis
            execution_flow = self._analyze_execution_flow(context)
            
            return {
                "entity_name": entity_name,
                "method_name": method_name,
                "file_location": context.get("file_path"),
                "analysis_timestamp": "2025-01-21T14:30:00Z",
                
                "purpose_analysis": purpose_analysis,
                "behavior_simulation": behavior_simulation,
                "risk_analysis": risk_analysis,
                "improvements": improvements,
                "execution_flow": execution_flow,
                
                "clarification_questions": self._generate_clarification_questions(context),
                "confidence_score": self._calculate_confidence_score(context)
            }
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "traceback": traceback.format_exc(),
                "debug_info": {
                    "entity_name": entity_name,
                    "method_name": method_name,
                    "file_path": file_path
                }
            }
    
    def _load_context(self, entity_name: str, method_name: Optional[str], file_path: Optional[str]) -> Dict[str, Any]:
        """Load full surrounding context for the given entity."""
        context = {
            "entity_name": entity_name,
            "method_name": method_name,
            "source_code": "",
            "ast_node": None,
            "file_path": "",
            "surrounding_context": {},
            "dependencies": [],
            "class_hierarchy": [],
            "module_info": {}
        }
        
        # Try different strategies to find the entity
        if file_path:
            # Strategy 1: Search in specific file
            context.update(self._search_in_file(Path(file_path), entity_name, method_name))
        else:
            # Strategy 2: Search in project files
            context.update(self._search_in_project(entity_name, method_name))
        
        if context["source_code"]:
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(context["source_code"])
                context["ast_node"] = self._find_ast_node(tree, entity_name, method_name)
                context["surrounding_context"] = self._extract_surrounding_context(tree, context["ast_node"])
            except SyntaxError as e:
                context["parse_error"] = str(e)
        
        return context
    
    def _search_in_file(self, file_path: Path, entity_name: str, method_name: Optional[str]) -> Dict[str, Any]:
        """Search for entity in a specific file."""
        try:
            if not file_path.exists():
                return {}
            
            content = file_path.read_text(encoding='utf-8')
            
            # Look for class or function definition
            pattern = rf"^(class|def)\s+{re.escape(entity_name)}\s*[\(\:]"
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                start_line = content[:match.start()].count('\n')
                
                # Extract the full definition (class or function)
                extracted_code = self._extract_full_definition(content, start_line)
                
                return {
                    "source_code": extracted_code,
                    "file_path": str(file_path),
                    "start_line": start_line,
                    "match_type": match.group(1)  # 'class' or 'def'
                }
                
        except Exception as e:
            return {"error": f"Error reading file {file_path}: {e}"}
        
        return {}
    
    def _search_in_project(self, entity_name: str, method_name: Optional[str]) -> Dict[str, Any]:
        """Search for entity across all Python files in the project."""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if file_path.name.startswith('.') or 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            result = self._search_in_file(file_path, entity_name, method_name)
            if result and result.get("source_code"):
                return result
        
        return {}
    
    def _extract_full_definition(self, content: str, start_line: int) -> str:
        """Extract the full class or function definition with proper indentation."""
        lines = content.split('\n')
        
        if start_line >= len(lines):
            return ""
        
        # Find the indentation level of the definition
        def_line = lines[start_line]
        base_indent = len(def_line) - len(def_line.lstrip())
        
        extracted_lines = [def_line]
        
        # Extract all lines that belong to this definition
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            
            # Empty lines or comments are included
            if not line.strip() or line.strip().startswith('#'):
                extracted_lines.append(line)
                continue
            
            # Check indentation
            current_indent = len(line) - len(line.lstrip())
            
            # If we're back to the same or less indentation, we've reached the end
            if current_indent <= base_indent and line.strip():
                break
                
            extracted_lines.append(line)
        
        return '\n'.join(extracted_lines)
    
    def _find_ast_node(self, tree: ast.AST, entity_name: str, method_name: Optional[str]) -> Optional[ast.AST]:
        """Find the specific AST node for the entity."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == entity_name:
                    if method_name and isinstance(node, ast.ClassDef):
                        # Look for specific method within the class
                        for child in node.body:
                            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method_name:
                                return child
                    return node
        return None
    
    def _extract_surrounding_context(self, tree: ast.AST, target_node: Optional[ast.AST]) -> Dict[str, Any]:
        """Extract surrounding context like imports, other classes, etc."""
        context = {
            "imports": [],
            "classes": [],
            "functions": [],
            "constants": [],
            "decorators": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                context["imports"].append(ast.unparse(node))
            elif isinstance(node, ast.ClassDef) and node != target_node:
                context["classes"].append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node != target_node:
                context["functions"].append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        context["constants"].append(target.id)
        
        return context
    
    def _analyze_purpose(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the purpose and intent of the code entity."""
        source_code = context.get("source_code", "")
        entity_name = context.get("entity_name", "")
        
        analysis = {
            "primary_purpose": "Unknown",
            "design_patterns": [],
            "responsibilities": [],
            "api_surface": {},
            "docstring_analysis": {},
            "naming_analysis": {}
        }
        
        # Extract docstring
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == entity_name:
                        docstring = ast.get_docstring(node)
                        if docstring:
                            analysis["docstring_analysis"] = {
                                "exists": True,
                                "length": len(docstring),
                                "has_parameters": "Args:" in docstring or "Parameters:" in docstring,
                                "has_returns": "Returns:" in docstring or "Return:" in docstring,
                                "has_examples": "Example" in docstring,
                                "content": docstring[:200] + "..." if len(docstring) > 200 else docstring
                            }
                        break
        except:
            pass
        
        # Analyze naming patterns
        analysis["naming_analysis"] = {
            "follows_convention": self._check_naming_convention(entity_name, context.get("match_type", "")),
            "descriptive": len(entity_name) > 3,
            "suggests_purpose": self._infer_purpose_from_name(entity_name)
        }
        
        # Identify design patterns
        if "class" in context.get("match_type", ""):
            analysis["design_patterns"] = self._identify_design_patterns(source_code)
        
        # Extract methods for API surface
        if context.get("ast_node"):
            analysis["api_surface"] = self._extract_api_surface(context["ast_node"])
        
        return analysis
    
    def _simulate_behavior(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate how the code behaves across different states and inputs."""
        simulation = {
            "state_transitions": [],
            "input_scenarios": [],
            "edge_cases": [],
            "error_conditions": [],
            "performance_characteristics": {},
            "side_effects": []
        }
        
        source_code = context.get("source_code", "")
        
        # Analyze control flow
        try:
            tree = ast.parse(source_code)
            simulation["state_transitions"] = self._analyze_control_flow(tree)
            simulation["error_conditions"] = self._identify_error_conditions(tree)
            simulation["side_effects"] = self._identify_side_effects(tree)
        except:
            pass
        
        # Generate test scenarios
        simulation["input_scenarios"] = self._generate_test_scenarios(context)
        simulation["edge_cases"] = self._identify_edge_cases(context)
        
        return simulation
    
    def _identify_risks_and_bugs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug the logic and identify potential risks or bugs."""
        risks = {
            "security_issues": [],
            "performance_issues": [],
            "correctness_issues": [],
            "maintainability_issues": [],
            "reliability_issues": [],
            "severity_levels": {}
        }
        
        source_code = context.get("source_code", "")
        
        # Security analysis
        risks["security_issues"] = self._analyze_security_risks(source_code)
        
        # Performance analysis  
        risks["performance_issues"] = self._analyze_performance_issues(source_code)
        
        # Correctness analysis
        risks["correctness_issues"] = self._analyze_correctness_issues(source_code)
        
        # Maintainability analysis
        risks["maintainability_issues"] = self._analyze_maintainability_issues(source_code)
        
        # Reliability analysis
        risks["reliability_issues"] = self._analyze_reliability_issues(source_code)
        
        # Assign severity levels
        all_issues = (risks["security_issues"] + risks["performance_issues"] + 
                     risks["correctness_issues"] + risks["maintainability_issues"] + 
                     risks["reliability_issues"])
        
        risks["severity_levels"] = {
            "critical": [issue for issue in all_issues if issue.get("severity") == "critical"],
            "high": [issue for issue in all_issues if issue.get("severity") == "high"],
            "medium": [issue for issue in all_issues if issue.get("severity") == "medium"],
            "low": [issue for issue in all_issues if issue.get("severity") == "low"]
        }
        
        return risks
    
    def _suggest_improvements(self, context: Dict[str, Any], risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest meaningful improvements based on analysis."""
        improvements = {
            "immediate_fixes": [],
            "refactoring_opportunities": [],
            "architectural_improvements": [],
            "testing_recommendations": [],
            "documentation_improvements": [],
            "prioritized_actions": []
        }
        
        # Generate improvements based on risks
        for category, issues in risk_analysis.items():
            if isinstance(issues, list):
                for issue in issues:
                    if isinstance(issue, dict) and "suggestion" in issue:
                        severity = issue.get("severity", "medium")
                        if severity in ["critical", "high"]:
                            improvements["immediate_fixes"].append(issue["suggestion"])
                        else:
                            improvements["refactoring_opportunities"].append(issue["suggestion"])
        
        # Add general improvements
        source_code = context.get("source_code", "")
        improvements["testing_recommendations"] = self._suggest_testing_improvements(context)
        improvements["documentation_improvements"] = self._suggest_documentation_improvements(context)
        improvements["architectural_improvements"] = self._suggest_architectural_improvements(context)
        
        # Prioritize actions
        improvements["prioritized_actions"] = self._prioritize_improvements(improvements)
        
        return improvements
    
    def _analyze_execution_flow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how the code will behave when executed step by step."""
        execution_flow = {
            "entry_points": [],
            "execution_path": [],
            "decision_points": [],
            "loops": [],
            "function_calls": [],
            "exception_handling": [],
            "resource_usage": {}
        }
        
        source_code = context.get("source_code", "")
        
        try:
            tree = ast.parse(source_code)
            
            # Trace execution flow
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    execution_flow["decision_points"].append({
                        "type": "if_statement",
                        "condition": ast.unparse(node.test) if hasattr(ast, 'unparse') else "condition",
                        "line": getattr(node, 'lineno', 0)
                    })
                elif isinstance(node, (ast.For, ast.While)):
                    execution_flow["loops"].append({
                        "type": type(node).__name__.lower(),
                        "line": getattr(node, 'lineno', 0)
                    })
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        execution_flow["function_calls"].append(node.func.id)
                elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                    execution_flow["exception_handling"].append({
                        "type": type(node).__name__.lower(),
                        "line": getattr(node, 'lineno', 0)
                    })
                    
        except:
            execution_flow["parse_error"] = "Could not parse execution flow"
        
        return execution_flow
    
    def _generate_clarification_questions(self, context: Dict[str, Any]) -> List[str]:
        """Generate questions to clarify unclear logic."""
        questions = []
        
        source_code = context.get("source_code", "")
        
        # Check for unclear naming
        if len(context.get("entity_name", "")) <= 3:
            questions.append(f"The name '{context.get('entity_name')}' is quite short. What does it represent?")
        
        # Check for missing docstring
        if not context.get("docstring_analysis", {}).get("exists"):
            questions.append("This code lacks documentation. What is its intended purpose and usage?")
        
        # Check for complex logic
        if source_code.count('if') > 3:
            questions.append("This code has multiple conditional branches. Are all edge cases handled correctly?")
        
        # Check for error handling
        if 'try' not in source_code and ('open(' in source_code or 'requests.' in source_code):
            questions.append("This code performs operations that might fail. Should error handling be added?")
        
        return questions
    
    def _calculate_confidence_score(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        score = 0.0
        
        # Base score for finding the code
        if context.get("source_code"):
            score += 30
        
        # Points for having documentation
        if context.get("docstring_analysis", {}).get("exists"):
            score += 20
        
        # Points for clear structure
        if context.get("ast_node"):
            score += 20
        
        # Points for context
        if context.get("surrounding_context", {}).get("imports"):
            score += 15
        
        # Points for file location
        if context.get("file_path"):
            score += 15
        
        return min(score, 100.0)
    
    # Helper methods for specific analysis tasks
    def _check_naming_convention(self, name: str, entity_type: str) -> bool:
        """Check if naming follows Python conventions."""
        if entity_type == "class":
            return name[0].isupper() and '_' not in name  # PascalCase
        else:
            return name.islower() or '_' in name  # snake_case
    
    def _infer_purpose_from_name(self, name: str) -> str:
        """Infer purpose from the entity name."""
        if any(word in name.lower() for word in ['manager', 'handler', 'controller']):
            return "Control/Management"
        elif any(word in name.lower() for word in ['parser', 'processor', 'analyzer']):
            return "Data Processing"
        elif any(word in name.lower() for word in ['client', 'service', 'api']):
            return "External Communication"
        elif any(word in name.lower() for word in ['validator', 'checker']):
            return "Validation"
        else:
            return "General Purpose"
    
    def _identify_design_patterns(self, source_code: str) -> List[str]:
        """Identify common design patterns in the code."""
        patterns = []
        
        if 'def __init__' in source_code and 'self.' in source_code:
            patterns.append("Constructor Pattern")
        
        if '@property' in source_code:
            patterns.append("Property Pattern")
        
        if 'def __enter__' in source_code and 'def __exit__' in source_code:
            patterns.append("Context Manager Pattern")
        
        if 'yield' in source_code:
            patterns.append("Generator Pattern")
        
        return patterns
    
    def _extract_api_surface(self, node: ast.AST) -> Dict[str, Any]:
        """Extract the public API surface of the entity."""
        api = {
            "public_methods": [],
            "private_methods": [],
            "properties": [],
            "class_variables": []
        }
        
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith('_'):
                        api["private_methods"].append(item.name)
                    else:
                        api["public_methods"].append(item.name)
                elif isinstance(item, ast.Assign):
                    # Class variable
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            api["class_variables"].append(target.id)
        
        return api
    
    def _analyze_control_flow(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze control flow patterns."""
        flow = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                flow.append({
                    "type": "conditional",
                    "complexity": len([n for n in ast.walk(node) if isinstance(n, ast.If)])
                })
            elif isinstance(node, (ast.For, ast.While)):
                flow.append({
                    "type": "loop",
                    "nested": len([n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))]) > 1
                })
        
        return flow
    
    def _identify_error_conditions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Identify potential error conditions."""
        errors = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                errors.append({"type": "IndexError", "description": "Potential index out of bounds"})
            elif isinstance(node, ast.Attribute):
                errors.append({"type": "AttributeError", "description": "Potential missing attribute"})
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['int', 'float']:
                    errors.append({"type": "ValueError", "description": "Type conversion might fail"})
        
        return errors
    
    def _identify_side_effects(self, tree: ast.AST) -> List[str]:
        """Identify potential side effects."""
        side_effects = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'print':
                    side_effects.append("Console output")
                elif node.func.id in ['open', 'write']:
                    side_effects.append("File system modification")
            elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Attribute) for target in node.targets):
                side_effects.append("Object state modification")
        
        return side_effects
    
    def _generate_test_scenarios(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test scenarios based on the code."""
        scenarios = [
            {"name": "Happy path", "description": "Normal execution with valid inputs"},
            {"name": "Edge cases", "description": "Boundary conditions and limit values"},
            {"name": "Error cases", "description": "Invalid inputs and error conditions"}
        ]
        
        return scenarios
    
    def _identify_edge_cases(self, context: Dict[str, Any]) -> List[str]:
        """Identify potential edge cases."""
        edge_cases = [
            "None/null inputs",
            "Empty collections",
            "Very large inputs",
            "Concurrent access",
            "Network failures (if applicable)"
        ]
        
        return edge_cases
    
    def _analyze_security_risks(self, source_code: str) -> List[Dict[str, Any]]:
        """Analyze security risks in the code."""
        risks = []
        
        if 'eval(' in source_code:
            risks.append({
                "type": "Code Injection",
                "description": "Use of eval() can execute arbitrary code",
                "severity": "critical",
                "suggestion": "Replace eval() with safer alternatives like ast.literal_eval()"
            })
        
        if 'open(' in source_code and 'w' in source_code:
            risks.append({
                "type": "File System Access",
                "description": "Writing to files without validation",
                "severity": "medium",
                "suggestion": "Validate file paths and implement proper access controls"
            })
        
        return risks
    
    def _analyze_performance_issues(self, source_code: str) -> List[Dict[str, Any]]:
        """Analyze performance issues."""
        issues = []
        
        if source_code.count('for') > 2 and 'in' in source_code:
            issues.append({
                "type": "Nested Loops",
                "description": "Multiple nested loops may cause performance issues",
                "severity": "medium",
                "suggestion": "Consider optimizing with list comprehensions or vectorized operations"
            })
        
        return issues
    
    def _analyze_correctness_issues(self, source_code: str) -> List[Dict[str, Any]]:
        """Analyze correctness issues."""
        issues = []
        
        if 'except:' in source_code:
            issues.append({
                "type": "Broad Exception Handling",
                "description": "Catching all exceptions can hide bugs",
                "severity": "high",
                "suggestion": "Catch specific exception types instead of using bare except"
            })
        
        return issues
    
    def _analyze_maintainability_issues(self, source_code: str) -> List[Dict[str, Any]]:
        """Analyze maintainability issues."""
        issues = []
        
        lines = source_code.split('\n')
        if len(lines) > 50:
            issues.append({
                "type": "Long Function/Class",
                "description": f"Entity has {len(lines)} lines, consider breaking it down",
                "severity": "medium",
                "suggestion": "Split into smaller, more focused functions or classes"
            })
        
        return issues
    
    def _analyze_reliability_issues(self, source_code: str) -> List[Dict[str, Any]]:
        """Analyze reliability issues."""
        issues = []
        
        if 'try:' not in source_code and ('requests.' in source_code or 'urllib' in source_code):
            issues.append({
                "type": "Missing Error Handling",
                "description": "Network operations without error handling",
                "severity": "high",
                "suggestion": "Add try-except blocks around network operations"
            })
        
        return issues
    
    def _suggest_testing_improvements(self, context: Dict[str, Any]) -> List[str]:
        """Suggest testing improvements."""
        suggestions = [
            "Add unit tests for each public method",
            "Include edge case testing",
            "Add integration tests if the code interacts with external systems",
            "Consider property-based testing for complex logic"
        ]
        
        return suggestions
    
    def _suggest_documentation_improvements(self, context: Dict[str, Any]) -> List[str]:
        """Suggest documentation improvements."""
        suggestions = []
        
        if not context.get("docstring_analysis", {}).get("exists"):
            suggestions.append("Add comprehensive docstring with purpose, parameters, and return values")
        
        suggestions.extend([
            "Add type hints for better code clarity",
            "Include usage examples in docstrings",
            "Document any side effects or dependencies"
        ])
        
        return suggestions
    
    def _suggest_architectural_improvements(self, context: Dict[str, Any]) -> List[str]:
        """Suggest architectural improvements."""
        suggestions = [
            "Consider applying SOLID principles",
            "Evaluate if the class/function has a single responsibility",
            "Consider dependency injection for better testability"
        ]
        
        return suggestions
    
    def _prioritize_improvements(self, improvements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize improvements by impact and effort."""
        prioritized = []
        
        # High priority: immediate fixes
        for fix in improvements.get("immediate_fixes", []):
            prioritized.append({
                "improvement": fix,
                "priority": "HIGH",
                "effort": "Low-Medium",
                "impact": "High"
            })
        
        # Medium priority: refactoring
        for refactor in improvements.get("refactoring_opportunities", []):
            prioritized.append({
                "improvement": refactor,
                "priority": "MEDIUM", 
                "effort": "Medium",
                "impact": "Medium"
            })
        
        return prioritized 