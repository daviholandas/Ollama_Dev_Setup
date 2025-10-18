#!/usr/bin/env python3
"""
Ollama Setup & Validation Script
=================================
Complete setup and validation tool for Ollama development environment.

Features:
- Cross-platform environment configuration (Linux/Windows/macOS)
- Model download and agent creation
- Setup validation and health checks
- Agent testing with performance metrics

Usage:
  # Setup
  python3 setup_ollama.py --global-env --threads 14
  python3 setup_ollama.py --persona arch,dev --pull --create
  
  # Validation
  python3 setup_ollama.py --validate
  python3 setup_ollama.py --validate --quick
  python3 setup_ollama.py --test-agent arch
  
  # Info
  python3 setup_ollama.py --list
  python3 setup_ollama.py --check-vram
"""

import argparse
import os
import sys
import subprocess
import platform
import time
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Persona metadata - used only for listing and validation
PERSONAS = {
    # Architecture agents
    "arch": {
        "modelfile": "arch-agent.Modelfile",
        "agent_name": "arch",
        "description": "Principal architect - DDD, microservices, cloud-native (qwen2.5:32b-instruct)"
    },
    "arch-ds": {
        "modelfile": "arch-agent-deepseek.Modelfile",
        "agent_name": "arch-ds",
        "description": "Architecture with chain-of-thought reasoning (deepseek-r1:32b)"
    },
    "arch14": {
        "modelfile": "arch-agent-qwen3_14b.Modelfile",
        "agent_name": "arch14",
        "description": "Architecture variant with Qwen3 14B (qqwen3:14b)"
    },
    "arch30": {
        "modelfile": "arch-agent-qwen3_30b.Modelfile",
        "agent_name": "arch30",
        "description": "Architecture variant with Qwen3 30B (qwen3:30b)"
    },
    "arch-coder": {
        "modelfile": "arch-agent-qwen3_coder.Modelfile",
        "agent_name": "arch-coder",
        "description": "Architecture with code focus (qwen3-coder:30b)"
    },
    
    # Development agents
    "dev": {
        "modelfile": "dev-agent.Modelfile",
        "agent_name": "dev",
        "description": "Code generation specialist - .NET, boilerplate (qwen2.5-coder:32b)"
    },
    "devq3": {
        "modelfile": "dev-agent-qw3.Modelfile",
        "agent_name": "devq3",
        "description": "Code generation with Qwen3 Coder 30B (qwen3-coder:30b)"
    },
    
    # Specialized agents
    "tester": {
        "modelfile": "test-agent.Modelfile",
        "agent_name": "tester",
        "description": "Test generation - unit, integration, e2e (qwen2.5-coder:14b-instruct)"
    },
    "planner": {
        "modelfile": "plan-agent.Modelfile",
        "agent_name": "planner",
        "description": "Detailed project planning and specifications (qwen2.5:14b-instruct)"
    },
    "plannerlite": {
        "modelfile": "planlite-agent.Modelfile",
        "agent_name": "plannerlite",
        "description": "Quick sprint planning and agile specs (qwen2.5:7b-instruct)"
    },
    "orch": {
        "modelfile": "orch-agent.Modelfile",
        "agent_name": "orch",
        "description": "Intelligent routing and task orchestration (qwen2.5:3b-instruct)"
    },
    "reviewer": {
        "modelfile": "review-agent.Modelfile",
        "agent_name": "reviewer",
        "description": "Code review - security, performance, best practices (qwen2.5-coder:14b-instruct)"
    },
    "debugger": {
        "modelfile": "debug-agent.Modelfile",
        "agent_name": "debugger",
        "description": "Root cause analysis and debugging (qwen2.5-coder:32b-instruct)"
    },
    "refactor": {
        "modelfile": "refactor-agent.Modelfile",
        "agent_name": "refactor",
        "description": "Code quality improvement and refactoring (qwen2.5-coder:14b-instruct)"
    },
    "docs": {
        "modelfile": "docs-agent.Modelfile",
        "agent_name": "docs",
        "description": "Technical documentation and API docs (qwen2.5:7b-instruct)"
    }
}

DEFAULT_ENVS = {
    "OLLAMA_NUM_GPU": "1",
    "OLLAMA_NUM_THREADS": "8",
    "OLLAMA_MAX_LOADED_MODELS": "1",
    "OLLAMA_KEEP_ALIVE": "5m",
    "CUDA_VISIBLE_DEVICES": "0",
    "OLLAMA_FLASH_ATTENTION": "1",
    "OLLAMA_MAX_QUEUE": "512"
}

# Validation test prompts
TEST_PROMPTS = {
    "arch": "Explain the CAP theorem in 50 words",
    "dev": "Create a simple C# class Person with Name and Age properties",
    "test": "Generate a unit test for a Calculator.Add(int a, int b) method"
}

def print_colored(text: str, color: str = Colors.RESET, bold: bool = False):
    """Print colored text to terminal"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.RESET}")
    else:
        print(f"{color}{text}{Colors.RESET}")

def print_header(text: str):
    """Print section header"""
    print()
    print_colored("=" * 60, Colors.CYAN)
    print_colored(text, Colors.CYAN, bold=True)
    print_colored("=" * 60, Colors.CYAN)
    print()

def print_success(text: str):
    """Print success message"""
    print_colored(f"✅ {text}", Colors.GREEN)

def print_error(text: str):
    """Print error message"""
    print_colored(f"❌ {text}", Colors.RED)

def print_warning(text: str):
    """Print warning message"""
    print_colored(f"⚠️  {text}", Colors.YELLOW)

def print_info(text: str):
    """Print info message"""
    print_colored(f"ℹ️  {text}", Colors.BLUE)

def have_ollama() -> bool:
    """Check if Ollama is installed"""
    try:
        subprocess.run(
            ["ollama", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except Exception:
        return False

def run_command(cmd: List[str], verbose: bool = True, timeout: int = 120) -> Tuple[bool, str]:
    """Execute command and return success status and output"""
    if verbose:
        print(f"$ {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timeout (>{timeout}s)"
    except Exception as e:
        return False, str(e)

def run_ollama_pull_with_progress(model: str, timeout: int = 1800) -> Tuple[bool, str]:
    """Execute ollama pull with live progress display"""
    print(f"$ ollama pull {model}")
    print()
    
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        start_time = time.time()
        last_line = ""
        
        # Track progress
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                process.kill()
                return False, f"Command timeout (>{timeout}s)"
            
            line = process.stdout.readline()
            if not line:
                break
            
            line = line.rstrip()
            if not line:
                continue
            
            output_lines.append(line)
            
            # Parse and display progress
            # Ollama outputs lines like: "pulling manifest", "pulling <hash>", "verifying sha256 digest"
            if "pulling" in line.lower() or "downloading" in line.lower():
                # Clear previous line and print new progress
                print(f"\r{Colors.BLUE}⬇️  {line}{Colors.RESET}", end="", flush=True)
                last_line = line
            elif "verifying" in line.lower():
                print(f"\r{Colors.CYAN}✓ {line}{Colors.RESET}")
                last_line = line
            elif "success" in line.lower():
                print(f"\r{Colors.GREEN}✓ {line}{Colors.RESET}")
                last_line = line
            elif line.strip():
                # Print other messages
                if last_line:
                    print()  # New line after progress
                print(f"{Colors.BLUE}  {line}{Colors.RESET}")
                last_line = ""
        
        # Wait for process to complete
        return_code = process.wait(timeout=10)
        
        if last_line:
            print()  # Final newline after progress
        
        full_output = "\n".join(output_lines)
        
        if return_code == 0:
            return True, full_output
        else:
            return False, full_output
            
    except subprocess.TimeoutExpired:
        return False, f"Command timeout (>{timeout}s)"
    except Exception as e:
        return False, str(e)

def get_ollama_list() -> str:
    """Get list of installed models/agents"""
    success, output = run_command(["ollama", "list"], verbose=False)
    return output if success else ""

def check_vram() -> Optional[Dict[str, int]]:
    """Check VRAM usage (NVIDIA only)"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", 
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True
        )
        used, total = map(int, result.stdout.strip().split(','))
        return {"used": used, "total": total, "percent": (used * 100) // total}
    except Exception:
        return None

def get_vram_recommendation(vram_mb: int) -> dict:
    """Get recommended configuration based on available VRAM"""
    recommendations = {
        8192: {  # 8GB
            "max_model": "14b",
            "gpu_layers": {"32b": 25, "30b": 20, "14b": 999, "7b": 999, "3b": 999}
        },
        12288: {  # 12GB
            "max_model": "32b (hybrid)",
            "gpu_layers": {"32b": 35, "30b": 30, "14b": 999, "7b": 999, "3b": 999}
        },
        16384: {  # 16GB
            "max_model": "32b",
            "gpu_layers": {"32b": 45, "30b": 40, "14b": 999, "7b": 999, "3b": 999}
        },
        24576: {  # 24GB
            "max_model": "72b (hybrid)",
            "gpu_layers": {"72b": 40, "32b": 999, "30b": 999, "14b": 999, "7b": 999, "3b": 999}
        }
    }
    
    # Find closest VRAM config
    for threshold in sorted(recommendations.keys()):
        if vram_mb <= threshold:
            return recommendations[threshold]
    
    # For >24GB
    return recommendations[24576]

def write_system_override(envs: Dict[str, str]):
    """Write systemd override for root installation"""
    override_dir = Path("/etc/systemd/system/ollama.service.d")
    override_dir.mkdir(parents=True, exist_ok=True)
    override = override_dir / "override.conf"
    lines = ["[Service]"] + [f'Environment="{k}={v}"' for k, v in envs.items()]
    override.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print_success(f"Wrote systemd override: {override}")
    print_info("Run: sudo systemctl daemon-reload && sudo systemctl restart ollama")

def write_user_profiles(envs: Dict[str, str]):
    """Write environment variables to user shell profiles"""
    home = Path.home()
    targets = [home / ".bashrc", home / ".zshrc", home / ".profile"]
    
    for t in targets:
        try:
            with open(t, "a", encoding="utf-8") as f:
                f.write("\n# Ollama Environment Configuration\n")
                for k, v in envs.items():
                    f.write(f"export {k}='{v}'\n")
            print_success(f"Appended envs to: {t}")
        except Exception as e:
            print_warning(f"Could not append to {t}: {e}")
    
    # Try user systemd
    try:
        override_dir = home / ".config/systemd/user/ollama.service.d"
        override_dir.mkdir(parents=True, exist_ok=True)
        override = override_dir / "override.conf"
        lines = ["[Service]"] + [f"Environment={k}={v}" for k, v in envs.items()]
        override.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print_success(f"Wrote user systemd override: {override}")
        print_info("Apply with: systemctl --user daemon-reload && systemctl --user restart ollama")
    except Exception as e:
        print_info(f"Systemd user override not created: {e}")

def write_windows_envs(envs: Dict[str, str]):
    """Write environment variables for Windows"""
    os.environ.update(envs)
    
    # Set via setx
    for k, v in envs.items():
        try:
            subprocess.run(["setx", k, str(v)], check=True)
            print_success(f"Set {k}={v}")
        except Exception as e:
            print_warning(f"setx failed for {k}: {e}")
    
    # Update PowerShell profile
    profile = os.path.expanduser("~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1")
    Path(profile).parent.mkdir(parents=True, exist_ok=True)
    with open(profile, "a", encoding="utf-8") as f:
        f.write("\n# Ollama Environment Configuration\n")
        for k, v in envs.items():
            f.write(f"$env:{k}='{v}'\n")
    print_success(f"PowerShell profile updated: {profile}")

def setup_environment(threads: int):
    """Configure environment variables"""
    print_header("ENVIRONMENT CONFIGURATION")
    
    envs = DEFAULT_ENVS.copy()
    envs["OLLAMA_NUM_THREADS"] = str(threads)
    
    os_name = platform.system().lower()
    
    if os_name == "windows":
        write_windows_envs(envs)
    else:
        is_root = (os.geteuid() == 0) if hasattr(os, "geteuid") else False
        if is_root:
            write_system_override(envs)
        else:
            write_user_profiles(envs)
    
    print()
    print_info("Environment variables configured!")
    if os_name != "windows":
        print_warning("Remember to reload shell: source ~/.bashrc")

def get_agent_name_from_modelfile(modelfile_path: Path) -> Optional[str]:
    """Extract agent name from Modelfile filename (removes .Modelfile extension)"""
    return modelfile_path.stem if modelfile_path.suffix == ".Modelfile" else None

def get_base_model_from_modelfile(modelfile_path: Path) -> Optional[str]:
    """Extract base model FROM directive from Modelfile"""
    try:
        with open(modelfile_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("FROM "):
                    return line.split("FROM ", 1)[1].strip()
    except Exception as e:
        print_error(f"Failed to read Modelfile: {e}")
    return None

def detect_model_size(model_name: str) -> Optional[str]:
    """Detect model size from model name (e.g., qwen3:30b -> '30b')"""
    # Common patterns: qwen2.5:32b, deepseek-r1:32b, qwen3:30b, etc.
    import re
    patterns = [
        r':(\d+)b',      # :30b, :32b, :14b
        r'-(\d+)b',      # -30b, -32b
        r'(\d+)b',       # 30b, 32b (standalone)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, model_name.lower())
        if match:
            return f"{match.group(1)}b"
    
    return None

def create_persona(persona: str, do_pull: bool, do_create: bool):
    """Download model and create agent strictly from Modelfile"""
    if persona not in PERSONAS:
        print_error(f"Unknown persona: {persona}")
        return False
    
    cfg = PERSONAS[persona]
    script_dir = Path(__file__).parent.resolve()
    modelfile_path = script_dir / "modelfiles" / cfg["modelfile"]
    
    if not modelfile_path.exists():
        print_error(f"Modelfile not found: {modelfile_path}")
        return False
    
    # Use custom agent name if specified, otherwise extract from Modelfile filename
    agent_name = cfg.get("agent_name")
    if not agent_name:
        agent_name = get_agent_name_from_modelfile(modelfile_path)
        if not agent_name:
            print_error(f"Could not determine agent name from: {modelfile_path.name}")
            return False
    
    # Extract base model from Modelfile
    base_model = get_base_model_from_modelfile(modelfile_path)
    if not base_model:
        print_error(f"No FROM directive found in {modelfile_path.name}")
        return False
    
    print_info(f"Persona: {persona}")
    print_info(f"Agent name: {agent_name}")
    print_info(f"Modelfile: {cfg['modelfile']}")
    print_info(f"Base model: {base_model}")
    
    if do_pull:
        print_info(f"Pulling base model: {base_model}")
        print_warning(f"This may take several minutes for large models (30B+ models can be ~20GB)")
        print()
        
        # Use pull with progress display (30 minute timeout)
        success, error_msg = run_ollama_pull_with_progress(base_model, timeout=1800)
        
        if not success:
            print()
            print_error(f"Failed to pull {base_model}")
            print_error(f"Error: {error_msg}")
            return False
        
        print()
        print_success(f"Model {base_model} pulled successfully!")
    
    if do_create:
        print_info(f"Creating agent: {agent_name}")
        
        # Detect model size for informational purposes
        model_size = detect_model_size(base_model)
        if model_size:
            print_info(f"Model size: {model_size}")
        
        # Check if Modelfile already has num_gpu parameter
        modelfile_content = modelfile_path.read_text()
        has_num_gpu = "PARAMETER num_gpu" in modelfile_content
        
        if has_num_gpu:
            print_info("Using custom num_gpu from Modelfile")
        else:
            print_success("Using Ollama's automatic GPU/CPU management")
            print_info("Ollama will optimize memory allocation for your hardware")
        
        print_info("Loading model and applying configuration...")
        
        # Show a simple spinner during agent creation
        print(f"{Colors.CYAN}⚙️  Processing", end="", flush=True)
        
        success, error_msg = run_command(
            ["ollama", "create", agent_name, "-f", str(modelfile_path)],
            verbose=False,
            timeout=300  # 5 minutes for large models
        )
        
        # Clear spinner line
        print(f"\r{' ' * 50}\r", end="", flush=True)
        
        if not success:
            print_error(f"Failed to create {agent_name}")
            print_error(f"Ollama error: {error_msg}")
            
            # Check for memory error
            if "memory layout cannot be allocated" in error_msg or "out of memory" in error_msg:
                print()
                print_warning("Memory allocation error detected!")
                print_info("This model may be too large for available VRAM. Suggestions:")
                print(f"  1. Try smaller quantization: q4_K_M instead of q5_K_M or q6_K")
                print(f"  2. Use smaller model variant (14B instead of 30B/32B)")
                print(f"  3. Close other applications to free VRAM")
                print(f"  4. Check current usage: nvidia-smi")
                print(f"  5. Stop running models: ollama stop --all")
            
            return False
        
        print_success(f"Agent '{agent_name}' created successfully!")
        print_info(f"Usage: ollama run {agent_name}")
    
    return True

def validate_models() -> Tuple[int, int]:
    """Validate installed base models by reading FROM directives in Modelfiles"""
    print_info("Checking installed base models...")
    print()
    
    script_dir = Path(__file__).parent.resolve()
    modelfiles_dir = script_dir / "modelfiles"
    ollama_list = get_ollama_list()
    required_models = set()
    
    # Scan all Modelfiles to extract required base models
    if modelfiles_dir.exists():
        for modelfile_path in modelfiles_dir.glob("*.Modelfile"):
            base_model = get_base_model_from_modelfile(modelfile_path)
            if base_model:
                required_models.add(base_model)
    
    found = 0
    total = len(required_models)
    
    for model in sorted(required_models):
        if model in ollama_list:
            print_success(f"{model}")
            found += 1
        else:
            print_error(f"{model} (missing)")
            print_info(f"   Run: ollama pull {model}")
    
    return found, total

def validate_agents() -> Tuple[int, int]:
    """Validate created agents by scanning Modelfiles directory"""
    print_info("Checking created agents...")
    print()
    
    script_dir = Path(__file__).parent.resolve()
    modelfiles_dir = script_dir / "modelfiles"
    ollama_list = get_ollama_list()
    
    found = 0
    total = 0
    
    if not modelfiles_dir.exists():
        print_error(f"Modelfiles directory not found: {modelfiles_dir}")
        return 0, 0
    
    # Scan all Modelfiles and check if corresponding agents exist
    for modelfile_path in sorted(modelfiles_dir.glob("*.Modelfile")):
        # Find persona configuration
        persona_id = None
        agent_name = None
        description = "No description"
        
        for pid, cfg in PERSONAS.items():
            if cfg["modelfile"] == modelfile_path.name:
                persona_id = pid
                agent_name = cfg.get("agent_name") or get_agent_name_from_modelfile(modelfile_path)
                description = cfg["description"]
                break
        
        # If not in PERSONAS, use filename
        if not agent_name:
            agent_name = get_agent_name_from_modelfile(modelfile_path)
        
        if not agent_name:
            continue
        
        total += 1
        
        if agent_name in ollama_list:
            print_success(f"{agent_name} - {description}")
            if persona_id:
                print_info(f"   Persona: {persona_id}")
            found += 1
        else:
            print_error(f"{agent_name} (missing)")
            print_info(f"   {description}")
            if persona_id:
                print_info(f"   Create with: python3 setup_ollama.py --persona {persona_id} --create")
            else:
                print_info(f"   Create with: ollama create {agent_name} -f {modelfile_path}")
    
    return found, total

def test_agent(agent_name: str, prompt: str, timeout: int = 60) -> Tuple[bool, float, str]:
    """Test agent with a prompt and measure performance"""
    print_info(f"Testing {agent_name}...")
    print_info(f"Prompt: '{prompt}'")
    print_info(f"Timeout: {timeout}s")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["ollama", "run", agent_name, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        elapsed = time.time() - start_time
        return True, elapsed, result.stdout
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return False, elapsed, "TIMEOUT"
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        return False, elapsed, f"ERROR: {e.stderr}"
    except Exception as e:
        elapsed = time.time() - start_time
        return False, elapsed, f"ERROR: {str(e)}"

def validate_setup(quick: bool = False):
    """Comprehensive setup validation"""
    print_header("SETUP VALIDATION")
    
    # Check Ollama installation
    print_info("Checking Ollama installation...")
    if have_ollama():
        success, version = run_command(["ollama", "--version"], verbose=False)
        if success:
            print_success(f"Ollama installed: {version.strip()}")
    else:
        print_error("Ollama not found!")
        print_info("Install from: https://ollama.ai/download")
        return False
    print()
    
    # Validate models
    models_found, models_total = validate_models()
    print()
    print_info(f"Models: {models_found}/{models_total} installed")
    print()
    
    # Validate agents
    agents_found, agents_total = validate_agents()
    print()
    print_info(f"Agents: {agents_found}/{agents_total} created")
    print()
    
    # Check VRAM
    print_info("Checking VRAM usage...")
    vram = check_vram()
    if vram:
        print_success(f"VRAM: {vram['used']}MB / {vram['total']}MB ({vram['percent']}%)")
        if vram['percent'] > 80:
            print_warning("VRAM usage high (>80%) - consider closing other processes")
    else:
        print_warning("nvidia-smi not found - skipping VRAM check")
    print()
    
    # Quick test (if not quick mode, skip)
    if not quick and agents_found > 0:
        print_header("AGENT QUICK TESTS")
        
        # Test arch-agent (critical)
        if "arch-agent" in get_ollama_list():
            success, elapsed, response = test_agent(
                "arch-agent",
                TEST_PROMPTS["arch"],
                timeout=60
            )
            
            if success:
                print_success(f"arch-agent responded in {elapsed:.1f}s")
                if elapsed < 30:
                    print_success("   Performance excellent!")
                elif elapsed < 60:
                    print_info("   Performance OK (expected for 72B)")
            else:
                print_error(f"arch-agent test failed: {response}")
            print()
        
        # Test dev-agent (stop sequences)
        if "dev-agent" in get_ollama_list():
            success, elapsed, response = test_agent(
                "dev-agent",
                TEST_PROMPTS["dev"],
                timeout=30
            )
            
            if success:
                print_success(f"dev-agent responded in {elapsed:.1f}s")
                # Check for multiple code blocks (stop sequence issue)
                if response.count("```") > 2:
                    print_warning("   Multiple code blocks detected - check stop sequences")
                else:
                    print_success("   Stop sequences working correctly")
            else:
                print_error(f"dev-agent test failed: {response}")
            print()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    all_good = (models_found == models_total and agents_found == agents_total)
    
    if all_good:
        print_success("All checks passed!")
    else:
        print_warning("Some components missing or misconfigured")
    
    print()
    print_info("Next steps:")
    if models_found < models_total:
        print("  1. Download missing models: python3 setup_ollama.py --persona <name> --pull")
    if agents_found < agents_total:
        print("  2. Create missing agents: python3 setup_ollama.py --persona <name> --create")
    print("  3. Test agents: python3 setup_ollama.py --test-agent <agent-name>")
    print()
    
    return all_good

def list_personas():
    """List available personas and their corresponding Modelfiles"""
    print_header("AVAILABLE PERSONAS")
    
    script_dir = Path(__file__).parent.resolve()
    modelfiles_dir = script_dir / "modelfiles"
    ollama_list = get_ollama_list()
    
    if not modelfiles_dir.exists():
        print_error(f"Modelfiles directory not found: {modelfiles_dir}")
        return
    
    # Group by category
    categories = {
        "Architecture": ["arch", "arch-deepseek", "arch-qwen3_14b", "arch-qwen3_30b", "arch-qwen3_coder"],
        "Development": ["dev", "dev-qw3"],
        "Quality": ["test", "review", "debug", "refactor"],
        "Planning": ["plan", "planlite"],
        "Other": ["orch", "docs"]
    }
    
    for category, persona_ids in categories.items():
        print_colored(f"\n{category}:", Colors.CYAN, bold=True)
        print()
        
        for persona_id in persona_ids:
            if persona_id not in PERSONAS:
                continue
            
            cfg = PERSONAS[persona_id]
            modelfile_path = modelfiles_dir / cfg["modelfile"]
            
            if not modelfile_path.exists():
                print_warning(f"{persona_id:20} - Modelfile missing: {cfg['modelfile']}")
                continue
            
            agent_name = cfg.get("agent_name") or get_agent_name_from_modelfile(modelfile_path)
            base_model = get_base_model_from_modelfile(modelfile_path)
            
            status = "✅ installed" if agent_name and agent_name in ollama_list else "❌ not installed"
            
            print(f"  {persona_id:20} → {agent_name or 'unknown':30} {status}")
            print(f"  {'':20}    {cfg['description']}")
            print(f"  {'':20}    Base: {base_model or 'unknown'}")
            print()
    
    print()
    print_info("To create an agent:")
    print("  python3 setup_ollama.py --persona <persona-id> --pull --create")
    print()
    print_info("To create all agents:")
    print("  python3 setup_ollama.py --persona arch,dev,test,plan,... --pull --create")


def main():
    parser = argparse.ArgumentParser(
        description="Ollama Setup & Validation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup environment
  python3 setup_ollama.py --global-env --threads 14
  
  # Download models and create agents
  python3 setup_ollama.py --persona arch,dev --pull --create
  
  # Validate installation
  python3 setup_ollama.py --validate
  python3 setup_ollama.py --validate --quick
  
  # Test specific agent
  python3 setup_ollama.py --test-agent arch
  
  # Information
  python3 setup_ollama.py --list
  python3 setup_ollama.py --check-vram
        """
    )
    
    # Setup arguments
    parser.add_argument("--global-env", action="store_true",
                       help="Configure environment variables")
    parser.add_argument("--threads", type=int, default=int(DEFAULT_ENVS["OLLAMA_NUM_THREADS"]),
                       help="Number of threads for OLLAMA_NUM_THREADS")
    parser.add_argument("--persona", type=str,
                       help="Comma-separated personas (dev,arch,test,etc)")
    parser.add_argument("--pull", action="store_true",
                       help="Download base models")
    parser.add_argument("--create", action="store_true",
                       help="Create agents from Modelfiles")
    
    # Validation arguments
    parser.add_argument("--validate", action="store_true",
                       help="Validate complete setup")
    parser.add_argument("--quick", action="store_true",
                       help="Quick validation (skip agent tests)")
    parser.add_argument("--test-agent", type=str, metavar="AGENT",
                       help="Test specific agent (e.g., arch-agent)")
    
    # Info arguments
    parser.add_argument("--list", action="store_true",
                       help="List available personas")
    parser.add_argument("--check-vram", action="store_true",
                       help="Check VRAM usage")
    
    args = parser.parse_args()
    
    # Show header
    print()
    print_colored("=" * 60, Colors.CYAN, bold=True)
    print_colored("🚀 OLLAMA SETUP & VALIDATION", Colors.CYAN, bold=True)
    print_colored("=" * 60, Colors.CYAN, bold=True)
    print()
    
    # Handle info commands
    if args.list:
        list_personas()
        return 0
    
    if args.check_vram:
        print_header("VRAM STATUS & RECOMMENDATIONS")
        vram = check_vram()
        if vram:
            print_success(f"Used: {vram['used']}MB")
            print_success(f"Total: {vram['total']}MB")
            print_success(f"Available: {vram['total'] - vram['used']}MB")
            print_success(f"Usage: {vram['percent']}%")
            
            if vram['percent'] > 80:
                print_warning("High VRAM usage - consider freeing memory")
            
            print()
            print_colored("Recommended GPU Layers for Your Setup:", Colors.CYAN, bold=True)
            print()
            
            vram_rec = get_vram_recommendation(vram['total'])
            print_info(f"Your GPU can handle models up to: {vram_rec['max_model']}")
            print()
            
            print("Model Size | GPU Layers | Mode")
            print("-" * 45)
            for size, layers in sorted(vram_rec['gpu_layers'].items(), key=lambda x: int(x[0].replace('b', ''))):
                mode = "Full GPU" if layers == 999 else "Hybrid GPU+CPU"
                print(f"  {size:8} | {layers:10} | {mode}")
            
            print()
            print_info("To apply these settings, add to your Modelfile:")
            print(f"  PARAMETER num_gpu <value>")
        else:
            print_error("nvidia-smi not available")
        return 0
    
    # Handle validation
    if args.validate:
        success = validate_setup(quick=args.quick)
        return 0 if success else 1
    
    # Handle agent testing
    if args.test_agent:
        if not have_ollama():
            print_error("Ollama not found!")
            return 1
        
        agent = args.test_agent
        # Use default prompt if available, otherwise ask user
        prompt = TEST_PROMPTS.get(agent.replace("-agent", ""), 
                                   "Explain your role in 50 words")
        
        print_header(f"TESTING {agent.upper()}")
        success, elapsed, response = test_agent(agent, prompt)
        
        if success:
            print_success(f"Test completed in {elapsed:.1f}s")
            print()
            print_info("Response:")
            print(response[:500])  # Show first 500 chars
            if len(response) > 500:
                print(f"... ({len(response)-500} more characters)")
            return 0
        else:
            print_error(f"Test failed: {response}")
            return 1
    
    # Check Ollama for persona operations
    if args.persona and not have_ollama():
        print_error("Ollama not found!")
        print_info("Install from: https://ollama.ai/download")
        return 1
    
    # Handle setup operations
    if args.global_env:
        setup_environment(args.threads)
    
    if args.persona:
        requested = [p.strip().lower() for p in args.persona.split(",") if p.strip()]
        invalid = [p for p in requested if p not in PERSONAS]
        
        if invalid:
            print_error(f"Invalid personas: {', '.join(invalid)}")
            print_info(f"Available: {', '.join(sorted(PERSONAS.keys()))}")
            print_info("Use --list to see all available personas with details")
            return 2
        
        print_header("PERSONA SETUP")
        
        for persona in requested:
            print()
            print_info(f"Processing: {persona}")
            print()
            
            success = create_persona(persona, args.pull, args.create)
            if success:
                print_success(f"✅ {persona} setup completed")
            else:
                print_error(f"❌ {persona} setup failed")
                return 1
            print()
        
        print_success("All persona setups completed!")
    
    # Show help if no action
    if not (args.global_env or args.persona or args.validate or args.test_agent):
        parser.print_help()
        return 0
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print_warning("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
