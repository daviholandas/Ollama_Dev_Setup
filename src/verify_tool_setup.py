#!/usr/bin/env python3
"""
verify_tool_setup.py - Verify VLLM tool-calling setup is configured correctly

This script checks:
- Docker Compose files have tool-calling flags
- Tool definition files exist and are valid JSON
- Python packages available
- VLLM agent connectivity
- Tool handler registration
"""

import json
import sys
from pathlib import Path
import subprocess
from typing import List, Tuple


class SetupVerifier:
    """Verify VLLM tool-calling setup"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.agents_dir = self.project_root / "agents"
        self.tools_dir = self.project_root / "tools"
        self.docs_dir = self.project_root / "docs"
        self.errors = []
        self.warnings = []
        self.success = []

    def log_success(self, msg: str):
        """Log success message"""
        self.success.append(msg)
        print(f"✅ {msg}")

    def log_warning(self, msg: str):
        """Log warning"""
        self.warnings.append(msg)
        print(f"⚠️ {msg}")

    def log_error(self, msg: str):
        """Log error"""
        self.errors.append(msg)
        print(f"❌ {msg}")

    def verify_docker_compose_files(self) -> bool:
        """Verify Docker Compose files have tool-calling flags"""
        print("\n📋 Checking Docker Compose files...")
        
        compose_files = {
            "architect": self.agents_dir / "docker-compose-architect.yml",
            "dev": self.agents_dir / "docker-compose-dev.yml",
            "po": self.agents_dir / "docker-compose-po.yml",
        }
        
        all_valid = True
        
        for name, file_path in compose_files.items():
            if not file_path.exists():
                self.log_error(f"Missing {file_path}")
                all_valid = False
                continue
            
            with open(file_path) as f:
                content = f.read()
            
            required_flags = [
                "VLLM_ENABLE_AUTO_TOOL_CHOICE=1",
                "VLLM_TOOL_CALL_PARSER=json",
                "--enable-auto-tool-choice",
                "--tool-call-parser json"
            ]
            
            missing_flags = [flag for flag in required_flags if flag not in content]
            
            if missing_flags:
                self.log_error(f"{name}: Missing flags: {missing_flags}")
                all_valid = False
            else:
                self.log_success(f"{name}: All tool-calling flags present")
        
        return all_valid

    def verify_tool_definition_files(self) -> bool:
        """Verify tool definition JSON files are valid"""
        print("\n📁 Checking tool definition files...")
        
        tool_files = {
            "architect": self.tools_dir / "architect-tools.json",
            "dev": self.tools_dir / "dev-tools.json",
            "po": self.tools_dir / "po-tools.json",
        }
        
        all_valid = True
        
        for name, file_path in tool_files.items():
            if not file_path.exists():
                self.log_error(f"Missing {file_path}")
                all_valid = False
                continue
            
            try:
                with open(file_path) as f:
                    tools = json.load(f)
                
                if not isinstance(tools, list):
                    self.log_error(f"{name}: Root must be an array")
                    all_valid = False
                    continue
                
                for i, tool in enumerate(tools):
                    if tool.get("type") != "function":
                        self.log_error(f"{name}[{i}]: type must be 'function'")
                        all_valid = False
                        continue
                    
                    if "function" not in tool:
                        self.log_error(f"{name}[{i}]: missing 'function' key")
                        all_valid = False
                
                self.log_success(f"{name}: {len(tools)} tools, valid JSON")
                
            except json.JSONDecodeError as e:
                self.log_error(f"{name}: Invalid JSON - {e}")
                all_valid = False
            except Exception as e:
                self.log_error(f"{name}: Error - {e}")
                all_valid = False
        
        return all_valid

    def verify_python_files(self) -> bool:
        """Verify Python framework files exist"""
        print("\n🐍 Checking Python files...")
        
        python_files = {
            "tool_integration.py": "Tool handler framework",
            "agent_tool_client.py": "Client library with tool support",
        }
        
        all_valid = True
        
        for filename, description in python_files.items():
            file_path = self.project_root / filename
            if not file_path.exists():
                self.log_error(f"Missing {filename}: {description}")
                all_valid = False
            else:
                self.log_success(f"{filename}: {description}")
        
        return all_valid

    def verify_documentation(self) -> bool:
        """Verify documentation files exist"""
        print("\n📖 Checking documentation...")
        
        doc_files = {
            "TOOL_CALLING_SETUP.md": "Comprehensive setup guide",
            "TOOL_CALLING_QUICK_REFERENCE.md": "Quick reference guide",
            "TOOL_CALLING_INTEGRATION_SUMMARY.md": "Integration summary",
        }
        
        all_valid = True
        
        for filename, description in doc_files.items():
            file_path = self.docs_dir / filename
            if not file_path.exists():
                self.log_error(f"Missing {filename}: {description}")
                all_valid = False
            else:
                self.log_success(f"{filename}: {description}")
        
        return all_valid

    def verify_python_packages(self) -> bool:
        """Verify required Python packages are available"""
        print("\n📦 Checking Python packages...")
        
        packages = ["requests", "docker"]
        all_valid = True
        
        for package in packages:
            try:
                __import__(package)
                self.log_success(f"{package}: Available")
            except ImportError:
                self.log_warning(f"{package}: Not installed (will be needed for runtime)")
                # This is not critical for verification
        
        return True

    def verify_agent_connectivity(self) -> bool:
        """Verify agents can be contacted (if running)"""
        print("\n🔌 Checking agent connectivity...")
        
        agents = {
            "architect": 8000,
            "dev": 8001,
            "po": 8002,
        }
        
        all_valid = True
        
        for name, port in agents.items():
            try:
                result = subprocess.run(
                    ["curl", "-s", "-f", f"http://localhost:{port}/v1/models"],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    self.log_success(f"{name} agent (:{port}): Running and responsive")
                else:
                    self.log_warning(f"{name} agent (:{port}): Not running (expected on first setup)")
            except subprocess.TimeoutExpired:
                self.log_warning(f"{name} agent (:{port}): Timeout (expected if not started)")
            except FileNotFoundError:
                self.log_warning("curl not found (skip connectivity test)")
                break
            except Exception as e:
                self.log_warning(f"{name} agent (:{port}): {e} (expected if not started)")
        
        return True

    def verify_tool_definitions_valid(self) -> bool:
        """Verify tool definitions follow OpenAI format"""
        print("\n🔧 Validating tool definition format...")
        
        tool_files = {
            "architect": self.tools_dir / "architect-tools.json",
            "dev": self.tools_dir / "dev-tools.json",
            "po": self.tools_dir / "po-tools.json",
        }
        
        all_valid = True
        
        for name, file_path in tool_files.items():
            if not file_path.exists():
                continue
            
            with open(file_path) as f:
                tools = json.load(f)
            
            for i, tool in enumerate(tools):
                func = tool.get("function", {})
                
                # Check required fields
                required = ["name", "description", "parameters"]
                missing = [field for field in required if field not in func]
                
                if missing:
                    self.log_error(f"{name}[{i}]: Missing required fields: {missing}")
                    all_valid = False
                    continue
                
                # Check parameters structure
                params = func.get("parameters", {})
                if params.get("type") != "object":
                    self.log_error(f"{name}[{i}]: parameters.type must be 'object'")
                    all_valid = False
                
                if not isinstance(params.get("properties"), dict):
                    self.log_error(f"{name}[{i}]: parameters.properties must be an object")
                    all_valid = False
            
            self.log_success(f"{name}: Tool definitions are valid")
        
        return all_valid

    def run_all_checks(self) -> Tuple[int, int, int]:
        """Run all verification checks"""
        print("=" * 60)
        print("🔍 VLLM Tool-Calling Setup Verification")
        print("=" * 60)
        
        self.verify_docker_compose_files()
        self.verify_tool_definition_files()
        self.verify_tool_definitions_valid()
        self.verify_python_files()
        self.verify_documentation()
        self.verify_python_packages()
        self.verify_agent_connectivity()
        
        print("\n" + "=" * 60)
        print("📊 Verification Summary")
        print("=" * 60)
        print(f"✅ Passed: {len(self.success)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\nErrors found:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        return len(self.success), len(self.warnings), len(self.errors)

    def print_next_steps(self):
        """Print next steps for setup"""
        print("\n" + "=" * 60)
        print("🚀 Next Steps")
        print("=" * 60)
        
        if not self.errors:
            print("""
1. Launch an agent with tool support:
   cd agents/
   docker-compose -f docker-compose-architect.yml up -d

2. Test tool-calling:
   python3 agent_tool_client.py architect

3. Integrate with your IDE:
   - Use agent_tool_client.py for API calls
   - Use tool_integration.py as handler template
   - Implement IDE-specific integrations

4. Monitor performance:
   watch -n 1 'nvidia-smi | head -20'
   docker logs vllm-architect-agent | grep -i tool

For more details, see:
  - docs/TOOL_CALLING_SETUP.md (comprehensive guide)
  - docs/TOOL_CALLING_QUICK_REFERENCE.md (quick start)
  - docs/TOOL_CALLING_INTEGRATION_SUMMARY.md (summary)
""")
        else:
            print("""
Please fix the errors listed above before proceeding.
Refer to docs/TOOL_CALLING_SETUP.md for troubleshooting.
""")


def main():
    """Main entry point"""
    verifier = SetupVerifier()
    success, warnings, errors = verifier.run_all_checks()
    verifier.print_next_steps()
    
    # Exit with error code if errors found
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
