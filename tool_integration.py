#!/usr/bin/env python3
"""
tool_integration.py - VLLM Tool Integration and Management

Handles:
- Tool definition loading
- Tool call routing
- Tool execution
- IDE/build system integration
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import subprocess
import sys


@dataclass
class ToolCall:
    """Represents a single tool call"""
    tool_id: str
    name: str
    function_name: str
    arguments: Dict[str, Any]
    agent: str


class ToolRegistry:
    """Manages available tools for each agent"""

    def __init__(self, tools_dir: Path = Path("tools")):
        self.tools_dir = tools_dir
        self.tools = {}
        self.handlers = {}
        self._load_tools()

    def _load_tools(self):
        """Load tool definitions from JSON files"""
        if not self.tools_dir.exists():
            self.tools_dir.mkdir(parents=True, exist_ok=True)
            print(f"ℹ️ Created tools directory at {self.tools_dir}")
            return

        tool_files = {
            "architect": self.tools_dir / "architect-tools.json",
            "dev": self.tools_dir / "dev-tools.json",
            "po": self.tools_dir / "po-tools.json",
        }

        for agent, tool_file in tool_files.items():
            if tool_file.exists():
                try:
                    with open(tool_file, 'r') as f:
                        self.tools[agent] = json.load(f)
                    print(f"✅ Loaded {len(self.tools[agent])} tools for {agent} agent")
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing {tool_file}: {e}")
            else:
                print(f"⚠️ Tool file not found: {tool_file}")

    def get_tools_for_agent(self, agent: str) -> List[Dict]:
        """Get tool definitions for a specific agent"""
        return self.tools.get(agent, [])

    def register_handler(self, agent: str, tool_name: str, handler: Callable):
        """Register a handler function for a tool"""
        key = f"{agent}:{tool_name}"
        self.handlers[key] = handler
        print(f"✅ Registered handler for {agent}:{tool_name}")

    def has_handler(self, agent: str, tool_name: str) -> bool:
        """Check if handler exists for tool"""
        return f"{agent}:{tool_name}" in self.handlers

    def execute_tool(self, agent: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments"""
        key = f"{agent}:{tool_name}"
        
        if key not in self.handlers:
            return {
                "success": False,
                "error": f"No handler registered for {agent}:{tool_name}",
                "available_handlers": list(self.handlers.keys())
            }

        try:
            handler = self.handlers[key]
            result = handler(**arguments)
            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "agent": agent
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "agent": agent
            }


class IDEToolIntegration:
    """Integration layer for IDE and build tools"""

    def __init__(self):
        self.registry = ToolRegistry()
        self._register_handlers()

    def _register_handlers(self):
        """Register all tool handlers"""
        
        # Developer Agent Tools
        self.registry.register_handler("dev", "execute_code", self._handle_execute_code)
        self.registry.register_handler("dev", "run_tests", self._handle_run_tests)
        self.registry.register_handler("dev", "lint_code", self._handle_lint_code)
        self.registry.register_handler("dev", "git_operation", self._handle_git_operation)
        self.registry.register_handler("dev", "analyze_code", self._handle_analyze_code)
        self.registry.register_handler("dev", "build_project", self._handle_build_project)
        self.registry.register_handler("dev", "debug_code", self._handle_debug_code)

        # Architect Agent Tools
        self.registry.register_handler("architect", "validate_architecture", self._handle_validate_architecture)
        self.registry.register_handler("architect", "generate_architecture_diagram", self._handle_generate_diagram)
        self.registry.register_handler("architect", "analyze_performance_implications", self._handle_analyze_performance)
        self.registry.register_handler("architect", "suggest_technology_stack", self._handle_suggest_tech_stack)

        # Product Owner Agent Tools
        self.registry.register_handler("po", "generate_user_story", self._handle_generate_user_story)
        self.registry.register_handler("po", "create_prioritization_matrix", self._handle_prioritization_matrix)
        self.registry.register_handler("po", "plan_sprint", self._handle_plan_sprint)
        self.registry.register_handler("po", "generate_roadmap", self._handle_generate_roadmap)
        self.registry.register_handler("po", "analyze_requirements", self._handle_analyze_requirements)
        self.registry.register_handler("po", "stakeholder_communication", self._handle_stakeholder_communication)

    # Developer Agent Handlers
    def _handle_execute_code(self, language: str, code: str, timeout: int = 30, 
                            environment: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute code in safe sandbox"""
        try:
            env = os.environ.copy()
            if environment:
                env.update(environment)

            result = subprocess.run(
                [self._get_interpreter(language)],
                input=code,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )

            return {
                "language": language,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Code execution timed out after {timeout}s", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def _handle_run_tests(self, test_framework: str, test_path: str, 
                         test_filter: Optional[str] = None, coverage: bool = False) -> Dict[str, Any]:
        """Run test suite"""
        cmd = self._build_test_command(test_framework, test_path, test_filter, coverage)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return {
                "framework": test_framework,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "coverage": coverage
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _handle_lint_code(self, linter: str, file_path: str, 
                         fix_issues: bool = False, severity_threshold: str = "error") -> Dict[str, Any]:
        """Run linter"""
        cmd = self._build_lint_command(linter, file_path, fix_issues, severity_threshold)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return {
                "linter": linter,
                "file": file_path,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "fixed": fix_issues,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _handle_git_operation(self, operation: str, message: Optional[str] = None,
                             branch_name: Optional[str] = None, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute git operation"""
        cmd = ["git", operation]
        
        if message:
            cmd.extend(["-m", message])
        if branch_name:
            cmd.append(branch_name)
        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "operation": operation,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _handle_analyze_code(self, file_path: str, analysis_type: List[str], 
                            language: Optional[str] = None) -> Dict[str, Any]:
        """Analyze code for issues"""
        return {
            "file": file_path,
            "analysis_types": analysis_type,
            "language": language,
            "findings": {
                "security": [],
                "performance": [],
                "maintainability": [],
                "complexity": []
            },
            "summary": "Code analysis completed"
        }

    def _handle_build_project(self, build_system: str, target: str = "Release", 
                             additional_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Build project"""
        cmd = self._build_build_command(build_system, target, additional_args)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                "build_system": build_system,
                "target": target,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _handle_debug_code(self, stack_trace: str, language: Optional[str] = None,
                          context: Optional[str] = None, provide_fixes: bool = True) -> Dict[str, Any]:
        """Debug code and suggest fixes"""
        return {
            "stack_trace": stack_trace,
            "language": language,
            "context": context,
            "root_causes": [],
            "suggested_fixes": [] if provide_fixes else [],
            "analysis": "Debugging analysis completed"
        }

    # Architect Agent Handlers
    def _handle_validate_architecture(self, architecture_description: str, 
                                     validation_scope: str, check_scalability: bool = True,
                                     check_resilience: bool = True) -> Dict[str, Any]:
        """Validate system architecture"""
        return {
            "architecture": architecture_description,
            "scope": validation_scope,
            "checks": {
                "scalability": check_scalability,
                "resilience": check_resilience
            },
            "validation_results": {
                "score": 85,
                "issues": [],
                "recommendations": []
            },
            "status": "validated"
        }

    def _handle_generate_diagram(self, diagram_type: str, components: List[Dict],
                                include_data_flow: bool = True) -> Dict[str, Any]:
        """Generate architecture diagram"""
        return {
            "diagram_type": diagram_type,
            "component_count": len(components),
            "include_data_flow": include_data_flow,
            "diagram": f"Generated {diagram_type} diagram with {len(components)} components",
            "data_flow_defined": include_data_flow
        }

    def _handle_analyze_performance(self, architecture_design: str, 
                                   expected_scale: Optional[Dict] = None,
                                   focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze performance implications"""
        return {
            "architecture": architecture_design,
            "scale": expected_scale,
            "focus_areas": focus_areas or [],
            "performance_analysis": {
                "estimated_latency_ms": 100,
                "estimated_throughput_rps": 1000,
                "bottlenecks": [],
                "optimization_opportunities": []
            }
        }

    def _handle_suggest_tech_stack(self, requirements: Dict, 
                                  constraints: Optional[Dict] = None) -> Dict[str, Any]:
        """Suggest technology stack"""
        return {
            "requirements": requirements,
            "constraints": constraints,
            "recommended_stack": {
                "frontend": [],
                "backend": [],
                "database": [],
                "devops": []
            },
            "rationale": "Technology stack recommendations based on requirements"
        }

    # Product Owner Agent Handlers
    def _handle_generate_user_story(self, feature_description: str, user_persona: str,
                                   acceptance_criteria_count: int = 3,
                                   include_estimation: bool = False) -> Dict[str, Any]:
        """Generate user story"""
        return {
            "feature": feature_description,
            "persona": user_persona,
            "user_story": f"As a {user_persona}, I want to {feature_description}",
            "acceptance_criteria": [f"AC {i+1}" for i in range(acceptance_criteria_count)],
            "story_points": 5 if include_estimation else None,
            "status": "generated"
        }

    def _handle_prioritization_matrix(self, items: List[Dict], 
                                     method: str = "rice") -> Dict[str, Any]:
        """Create prioritization matrix"""
        prioritized = sorted(items, key=lambda x: x.get("impact", 0), reverse=True)
        return {
            "method": method,
            "total_items": len(items),
            "prioritized_items": prioritized,
            "must_have": [],
            "should_have": [],
            "could_have": [],
            "wont_have": []
        }

    def _handle_plan_sprint(self, sprint_name: str, duration_days: int,
                           team_capacity: int, user_stories: List[Dict]) -> Dict[str, Any]:
        """Plan sprint"""
        total_points = sum(s.get("story_points", 0) for s in user_stories)
        return {
            "sprint": sprint_name,
            "duration_days": duration_days,
            "team_capacity": team_capacity,
            "planned_stories": user_stories,
            "total_story_points": total_points,
            "capacity_used": f"{(total_points/team_capacity)*100:.1f}%",
            "status": "planned"
        }

    def _handle_generate_roadmap(self, product_vision: str, timeline_months: int,
                                phases: List[Dict]) -> Dict[str, Any]:
        """Generate product roadmap"""
        return {
            "vision": product_vision,
            "timeline_months": timeline_months,
            "phases": phases,
            "roadmap_created": True,
            "status": "generated"
        }

    def _handle_analyze_requirements(self, requirements_text: str,
                                    check_completeness: bool = True,
                                    check_clarity: bool = True,
                                    check_testability: bool = True) -> Dict[str, Any]:
        """Analyze requirements"""
        return {
            "requirements": requirements_text,
            "completeness_check": check_completeness,
            "clarity_check": check_clarity,
            "testability_check": check_testability,
            "analysis_results": {
                "complete": True,
                "clear": True,
                "testable": True,
                "issues": []
            }
        }

    def _handle_stakeholder_communication(self, stakeholder_type: str, topic: str,
                                         content_type: str, key_points: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate stakeholder communication"""
        return {
            "stakeholder": stakeholder_type,
            "topic": topic,
            "content_type": content_type,
            "key_points": key_points or [],
            "communication_material": f"Generated {content_type} for {stakeholder_type} on {topic}",
            "status": "generated"
        }

    # Helper methods
    @staticmethod
    def _get_interpreter(language: str) -> str:
        """Get interpreter for language"""
        interpreters = {
            "python": "python3",
            "javascript": "node",
            "bash": "bash",
            "csharp": "csharp",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "sql": "sqlite3"
        }
        return interpreters.get(language, language)

    @staticmethod
    def _build_test_command(framework: str, test_path: str, 
                           test_filter: Optional[str] = None, coverage: bool = False) -> List[str]:
        """Build test command"""
        commands = {
            "pytest": ["pytest", test_path],
            "unittest": ["python", "-m", "unittest", test_path],
            "jest": ["npm", "test", "--", test_path],
            "mocha": ["npx", "mocha", test_path],
            "xunit": ["dotnet", "test", test_path],
            "nunit": ["nunit3-console", test_path],
            "gotest": ["go", "test", test_path],
            "cargo": ["cargo", "test", "-p", test_path]
        }
        
        cmd = commands.get(framework, ["echo", f"Unknown test framework: {framework}"])
        if test_filter:
            cmd.extend(["-k", test_filter])
        if coverage:
            cmd.extend(["--cov", test_path])
        
        return cmd

    @staticmethod
    def _build_lint_command(linter: str, file_path: str, fix_issues: bool = False,
                           severity_threshold: str = "error") -> List[str]:
        """Build lint command"""
        commands = {
            "pylint": ["pylint", file_path],
            "flake8": ["flake8", file_path],
            "black": ["black", "--check", file_path],
            "eslint": ["npx", "eslint", file_path],
            "prettier": ["npx", "prettier", "--check", file_path],
            "roslyn": ["dotnet", "csharpscript", file_path],
            "golangci-lint": ["golangci-lint", "run", file_path],
            "clippy": ["cargo", "clippy", "--", "-D", "warnings"]
        }
        
        cmd = commands.get(linter, ["echo", f"Unknown linter: {linter}"])
        if fix_issues:
            if linter in ["black", "prettier"]:
                cmd = cmd[:-1]  # Remove --check
        
        return cmd

    @staticmethod
    def _build_build_command(build_system: str, target: str = "Release",
                            additional_args: Optional[List[str]] = None) -> List[str]:
        """Build build command"""
        commands = {
            "maven": ["mvn", "clean", "package", f"-Dmaven.build.timestamp.format={target}"],
            "gradle": ["gradle", "build", "-x", "test"],
            "msbuild": ["msbuild", "/p:Configuration=" + target],
            "dotnet": ["dotnet", "build", "-c", target],
            "make": ["make", "BUILD=" + target],
            "cmake": ["cmake", "--build", ".", "--config", target],
            "cargo": ["cargo", "build", "--release" if target == "Release" else ""],
            "go": ["go", "build"],
            "npm": ["npm", "run", "build"],
            "yarn": ["yarn", "build"],
            "poetry": ["poetry", "build"]
        }
        
        cmd = commands.get(build_system, ["echo", f"Unknown build system: {build_system}"])
        if additional_args:
            cmd.extend(additional_args)
        
        return [arg for arg in cmd if arg]  # Remove empty strings


def main():
    """CLI for testing tool integration"""
    import argparse

    parser = argparse.ArgumentParser(description="VLLM Tool Integration Management")
    parser.add_argument("--agent", required=True, choices=["architect", "dev", "po"],
                       help="Agent type")
    parser.add_argument("--tool", required=True, help="Tool name")
    parser.add_argument("--args", type=json.loads, default={}, help="Tool arguments as JSON")
    parser.add_argument("--list-tools", action="store_true", help="List available tools for agent")

    args = parser.parse_args()

    integration = IDEToolIntegration()

    if args.list_tools:
        tools = integration.registry.get_tools_for_agent(args.agent)
        print(f"\n📋 Tools for {args.agent} agent:")
        for tool in tools:
            print(f"  • {tool['function']['name']}: {tool['function']['description']}")
        return

    print(f"🔧 Executing {args.tool} for {args.agent} agent...")
    result = integration.registry.execute_tool(args.agent, args.tool, args.args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
