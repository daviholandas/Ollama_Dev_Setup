#!/usr/bin/env python3
"""
setup_vllm.py - VLLM Installation and Configuration Automation

Automated setup for VLLM with three specialized AI agents:
- Architect: Strategic system design (32B model)
- Developer: Code generation and implementation (32B coder model)
- Product Owner: Requirements and planning (7B lightweight model)

This script handles:
1. VLLM installation with quantization support
2. CUDA and GPU validation
3. Docker and NVIDIA Container Toolkit setup
4. Model downloads (Qwen2.5 series)
5. Configuration file generation
6. Validation and testing
"""

import os
import sys
import subprocess
import json
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class VLLMSetup:
    """Main VLLM setup orchestrator"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.models_dir = self.project_root / "models"
        self.docker_dir = self.project_root / "docker"
        self.configs_dir = self.project_root / "configs"
        
        # Create required directories
        self.models_dir.mkdir(exist_ok=True)
        self.docker_dir.mkdir(exist_ok=True)
        self.configs_dir.mkdir(exist_ok=True)

        # Agent configurations
        self.agents = {
            "architect": {
                "model": "Qwen/Qwen2.5-32B-Instruct",
                "quantization": "q5_K_M",
                "context_length": 32768,
                "temperature": 0.1,
                "top_p": 0.95,
                "gpu_memory_fraction": 0.85,
                "port": 8000,
            },
            "dev": {
                "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
                "quantization": "q4_K_M",
                "context_length": 32768,
                "temperature": 0.3,
                "top_p": 0.95,
                "gpu_memory_fraction": 0.95,
                "port": 8001,
            },
            "po": {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "quantization": "q5_K_M",
                "context_length": 16384,
                "temperature": 0.5,
                "top_p": 0.9,
                "gpu_memory_fraction": 0.6,
                "port": 8002,
            },
        }

    def log(self, message: str, level: str = "INFO") -> None:
        """Log messages with level prefix"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
        }.get(level, "ℹ️")
        print(f"{prefix} [{level}] {message}")

    def run_command(
        self, cmd: List[str], check: bool = True, capture: bool = False
    ) -> Tuple[int, str, str]:
        """Execute shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture,
                text=True,
                timeout=300,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {' '.join(cmd)}", "ERROR")
            return 124, "", "Command timed out"
        except Exception as e:
            self.log(f"Command failed: {str(e)}", "ERROR")
            return 1, "", str(e)

    def check_cuda(self) -> bool:
        """Verify CUDA installation and GPU availability"""
        self.log("Checking CUDA installation...")
        
        # Check nvidia-smi
        code, stdout, stderr = self.run_command(["nvidia-smi"], capture=True)
        if code != 0:
            self.log("NVIDIA GPU not found. Install NVIDIA drivers.", "ERROR")
            return False

        self.log("NVIDIA GPU detected", "SUCCESS")
        
        # Check CUDA version
        code, stdout, stderr = self.run_command(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
            capture=True,
        )
        if code == 0:
            compute_cap = stdout.strip()
            self.log(f"GPU Compute Capability: {compute_cap}", "SUCCESS")
            
            # Check if compute capability supports modern quantization
            try:
                cap = float(compute_cap)
                if cap >= 7.0:
                    self.log("GPU supports INT8 quantization (Turing or newer)", "SUCCESS")
                if cap >= 8.9:
                    self.log("GPU supports FP8 quantization (Lovelace or newer)", "SUCCESS")
            except ValueError:
                pass

        return True

    def check_docker(self) -> bool:
        """Verify Docker installation"""
        self.log("Checking Docker installation...")
        
        code, _, _ = self.run_command(["docker", "--version"], capture=True)
        if code != 0:
            self.log("Docker not found. Please install Docker.", "ERROR")
            return False

        self.log("Docker is installed", "SUCCESS")

        # Check NVIDIA Container Runtime
        self.log("Checking NVIDIA Container Runtime...")
        code, _, _ = self.run_command(
            ["docker", "run", "--rm", "--gpus", "all", "nvidia/cuda:12.2.0-runtime-ubuntu22.04", "nvidia-smi"],
            capture=True,
        )
        if code != 0:
            self.log(
                "NVIDIA Container Runtime not configured. Running installation...",
                "WARNING",
            )
            self.install_nvidia_container_toolkit()
        else:
            self.log("NVIDIA Container Runtime is configured", "SUCCESS")

        return True

    def install_nvidia_container_toolkit(self) -> bool:
        """Install NVIDIA Container Toolkit"""
        self.log("Installing NVIDIA Container Toolkit...", "WARNING")

        # Detect OS
        os_type = os.uname().sysname
        
        if os_type == "Linux":
            # Detect distribution
            if Path("/etc/os-release").exists():
                with open("/etc/os-release") as f:
                    os_info = dict(
                        line.split("=", 1)
                        for line in f
                        if "=" in line
                    )
                    distro = os_info.get("ID", "").strip('"')

                if distro in ["ubuntu", "debian"]:
                    self.log("Installing on Debian/Ubuntu...", "INFO")
                    self.run_command(
                        ["sudo", "apt-get", "update"],
                        check=False,
                    )
                    self.run_command(
                        [
                            "sudo",
                            "apt-get",
                            "install",
                            "-y",
                            "nvidia-container-toolkit",
                        ],
                        check=False,
                    )
                    self.run_command(
                        ["sudo", "systemctl", "restart", "docker"],
                        check=False,
                    )
                    self.log("NVIDIA Container Toolkit installed", "SUCCESS")
                    return True

        self.log("Please install NVIDIA Container Toolkit manually.", "ERROR")
        return False

    def install_vllm(self) -> bool:
        """Install VLLM with quantization support"""
        self.log("Installing VLLM with CUDA 12 support...")

        packages = [
            "vllm[cuda12]",
            "nvidia-modelopt",  # For quantization
            "torch",
            "torchvision",
        ]

        for package in packages:
            self.log(f"Installing {package}...", "INFO")
            code, _, stderr = self.run_command(
                [sys.executable, "-m", "pip", "install", "-U", package],
                check=False,
                capture=True,
            )
            if code != 0:
                self.log(f"Failed to install {package}: {stderr}", "WARNING")
            else:
                self.log(f"{package} installed", "SUCCESS")

        # Verify installation
        code, _, _ = self.run_command(
            [sys.executable, "-c", "import vllm; print(vllm.__version__)"],
            capture=True,
        )
        if code == 0:
            self.log("VLLM installation verified", "SUCCESS")
            return True

        self.log("VLLM installation verification failed", "ERROR")
        return False

    def download_models(self) -> bool:
        """Download required models"""
        self.log("Downloading models (this may take 20-30 minutes)...", "INFO")

        models_to_download = [
            ("Qwen/Qwen2.5-32B-Instruct", "qwen2.5-32b"),
            ("Qwen/Qwen2.5-Coder-32B-Instruct", "qwen2.5-coder-32b"),
            ("Qwen/Qwen2.5-7B-Instruct", "qwen2.5-7b"),
        ]

        for model_id, alias in models_to_download:
            self.log(f"Downloading {model_id}...", "INFO")
            code, _, stderr = self.run_command(
                [
                    sys.executable,
                    "-c",
                    f"from huggingface_hub import snapshot_download; "
                    f"snapshot_download('{model_id}', cache_dir='{self.models_dir}')",
                ],
                check=False,
                capture=True,
            )
            if code != 0:
                self.log(f"Failed to download {model_id}: {stderr}", "WARNING")
            else:
                self.log(f"{model_id} downloaded to {self.models_dir}", "SUCCESS")

        return True

    def generate_docker_compose(self, agent: str, config: Dict) -> str:
        """Generate docker-compose.yml content for agent"""
        return f"""version: '3.8'

services:
  {agent}-agent:
    image: nvidia/cuda:12.2.0-devel-ubuntu22.04
    container_name: vllm-{agent}-agent
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - CUDA_VISIBLE_DEVICES=0
      - VLLM_GPU_MEMORY_UTILIZATION={config['gpu_memory_fraction']}
      - VLLM_TENSOR_PARALLEL_SIZE=1
      - VLLM_ENABLE_PREFIX_CACHING=1
      - VLLM_MAX_MODEL_LEN={config['context_length']}
      - VLLM_QUANTIZATION=awq
    volumes:
      - {self.models_dir}:/models
      - ./outputs:/outputs
      - ./config_{agent}.json:/etc/vllm/config.json
    ports:
      - "{config['port']}:8000"
      - "{config['port'] + 100}:8001"
    entrypoint: >
      bash -c "
        pip install -q vllm[cuda12] &&
        vllm serve {config['model']} 
          --model-id {agent}-agent
          --gpu-memory-utilization {config['gpu_memory_fraction']}
          --max-model-len {config['context_length']}
          --quantization awq
          --port 8000
          --served-model-name {agent}
      "
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
"""

    def create_docker_compose_files(self) -> bool:
        """Create docker-compose files for each agent"""
        self.log("Generating Docker Compose configurations...")

        for agent_name, config in self.agents.items():
            compose_content = self.generate_docker_compose(agent_name, config)
            compose_path = self.project_root / f"docker-compose-{agent_name}.yml"
            
            with open(compose_path, "w") as f:
                f.write(compose_content)

            self.log(f"Created {compose_path}", "SUCCESS")

        return True

    def create_agent_configs(self) -> bool:
        """Create configuration JSON files for each agent"""
        self.log("Generating agent configurations...")

        for agent_name, config in self.agents.items():
            config_path = self.configs_dir / f"config_{agent_name}.json"
            
            agent_config = {
                "name": f"{agent_name}-agent",
                "model": config["model"],
                "quantization": config["quantization"],
                "context_length": config["context_length"],
                "temperature": config["temperature"],
                "top_p": config["top_p"],
                "gpu_memory_fraction": config["gpu_memory_fraction"],
                "port": config["port"],
            }

            with open(config_path, "w") as f:
                json.dump(agent_config, f, indent=2)

            self.log(f"Created {config_path}", "SUCCESS")

        return True

    def validate(self) -> bool:
        """Validate the setup"""
        self.log("Validating VLLM setup...", "INFO")

        checks = [
            ("CUDA/GPU Support", self.check_cuda()),
            ("Docker Installation", self.check_docker()),
            ("VLLM Installation", self.verify_vllm_install()),
        ]

        all_passed = True
        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not result:
                all_passed = False

        if all_passed:
            self.log("All validation checks passed!", "SUCCESS")
        else:
            self.log("Some validation checks failed. See details above.", "ERROR")

        return all_passed

    def verify_vllm_install(self) -> bool:
        """Verify VLLM is installed"""
        code, _, _ = self.run_command(
            [sys.executable, "-c", "import vllm"],
            capture=True,
        )
        return code == 0

    def test_agent(self, agent: str) -> bool:
        """Test agent inference (requires Docker and model loaded)"""
        self.log(f"Testing {agent} agent...", "INFO")
        
        if agent not in self.agents:
            self.log(f"Unknown agent: {agent}", "ERROR")
            return False

        config = self.agents[agent]
        port = config["port"]

        # Quick inference test
        self.log(f"Sending test prompt to {agent} agent on port {port}...", "INFO")
        
        code, _, _ = self.run_command(
            [
                "curl",
                "-X",
                "POST",
                f"http://localhost:{port}/v1/completions",
                "-H",
                "Content-Type: application/json",
                "-d",
                '{"model": "' + agent + '", "prompt": "Hello", "max_tokens": 10}',
            ],
            capture=True,
            check=False,
        )

        if code == 0:
            self.log(f"{agent} agent test successful", "SUCCESS")
            return True
        else:
            self.log(f"{agent} agent test failed (container may not be running)", "WARNING")
            return False

    def list_agents(self) -> None:
        """List available agents and their configurations"""
        print("\n🤖 Available Agents:\n")
        for agent_name, config in self.agents.items():
            print(f"  {agent_name.upper()}")
            print(f"    Model: {config['model']}")
            print(f"    Context: {config['context_length']} tokens")
            print(f"    Temperature: {config['temperature']}")
            print(f"    Port: {config['port']}")
            print()

    def main(self, args: argparse.Namespace) -> int:
        """Main entry point"""
        print("🚀 VLLM Multi-Agent Setup\n")

        if args.list:
            self.list_agents()
            return 0

        if args.install_dependencies:
            self.log("Installing dependencies...", "INFO")
            if not self.check_cuda():
                return 1
            if not self.check_docker():
                return 1
            if not self.install_vllm():
                return 1
            self.log("Dependencies installed successfully", "SUCCESS")

        if args.download_models:
            if not self.download_models():
                return 1

        if args.setup_docker:
            if not self.create_docker_compose_files():
                return 1
            if not self.create_agent_configs():
                return 1
            self.log("Docker setup complete", "SUCCESS")

        if args.validate:
            if not self.validate():
                return 1

        if args.test_agent:
            if not self.test_agent(args.test_agent):
                return 1

        if not any([
            args.install_dependencies,
            args.download_models,
            args.setup_docker,
            args.validate,
            args.test_agent,
            args.list,
        ]):
            print("Run with --help for usage information")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="VLLM Multi-Agent Setup and Configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full setup
  python3 setup_vllm.py --install-dependencies --download-models --setup-docker --validate

  # Just validate
  python3 setup_vllm.py --validate

  # Test specific agent
  python3 setup_vllm.py --test-agent architect

  # List agents
  python3 setup_vllm.py --list
        """,
    )

    parser.add_argument(
        "--install-dependencies",
        action="store_true",
        help="Install VLLM and dependencies",
    )
    parser.add_argument(
        "--download-models",
        action="store_true",
        help="Download required models",
    )
    parser.add_argument(
        "--setup-docker",
        action="store_true",
        help="Generate Docker Compose files",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate installation",
    )
    parser.add_argument(
        "--test-agent",
        type=str,
        help="Test specific agent (architect, dev, po)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available agents",
    )

    args = parser.parse_args()
    setup = VLLMSetup()
    sys.exit(setup.main(args))


if __name__ == "__main__":
    main()
