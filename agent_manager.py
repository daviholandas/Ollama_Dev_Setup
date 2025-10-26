#!/usr/bin/env python3
"""
agent_manager.py - Multi-Agent Docker Container Management CLI

Unified CLI for launching, stopping, and managing three specialized AI agents:
- Architect: Strategic system design
- Developer: Code generation and implementation
- Product Owner: Requirements and planning

Features:
- Launch specific agents
- Switch between agents (stop current, launch new)
- Monitor GPU memory usage
- View agent logs
- Health checks
- State management
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime

import docker
from docker import DockerClient
from docker.errors import DockerException, APIError
from docker.types import DeviceRequest


class AgentManager:
    """Docker-based agent lifecycle management"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.state_file = self.project_root / ".agent_state.json"
        self.models_dir = self.project_root / "models"
        self.outputs_dir = self.project_root / "outputs"

        # Create required directories
        self.models_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)

        # Agent configurations
        self.agents = {
            "architect": {
                "compose_file": "docker-compose-architect.yml",
                "container_name": "vllm-architect-agent",
                "model": "Qwen/Qwen2.5-32B-Instruct",
                "port": 8000,
                "gpu_memory": "~13.2GB",
                "context_length": "32K",
            },
            "dev": {
                "compose_file": "docker-compose-dev.yml",
                "container_name": "vllm-dev-agent",
                "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
                "port": 8001,
                "gpu_memory": "~14.8GB",
                "context_length": "32K",
            },
            "po": {
                "compose_file": "docker-compose-po.yml",
                "container_name": "vllm-po-agent",
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "port": 8002,
                "gpu_memory": "~3.5GB",
                "context_length": "16K",
            },
        }

        try:
            self.docker_client: DockerClient = docker.from_env()
        except DockerException:
            self.log(
                "Failed to connect to Docker daemon. Is Docker running?", "ERROR"
            )
            sys.exit(1)

    def log(self, message: str, level: str = "INFO") -> None:
        """Log with level prefix and timestamp"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "WARN": "⚠️",
        }.get(level, "ℹ️")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{prefix} [{timestamp}] [{level}] {message}")

    def save_state(self, agent: str) -> None:
        """Save agent state to file"""
        state = {
            "current_agent": agent,
            "timestamp": datetime.now().isoformat(),
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> Optional[str]:
        """Load agent state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                return state.get("current_agent")
            except json.JSONDecodeError:
                return None
        return None

    def list_agents(self) -> None:
        """Display all available agents"""
        print("\n🤖 Available Agents:\n")
        for agent_name, config in self.agents.items():
            print(f"  {agent_name.upper():12} | {config['model']}")
            print(f"  {'':12} | Port: {config['port']}, Memory: {config['gpu_memory']}")
            print()

    def get_container(self, agent: str) -> Optional[docker.models.containers.Container]:
        """Get container object for agent"""
        if agent not in self.agents:
            self.log(f"Unknown agent: {agent}", "ERROR")
            return None

        container_name = self.agents[agent]["container_name"]
        try:
            return self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            return None

    def container_exists(self, agent: str) -> bool:
        """Check if agent container exists"""
        return self.get_container(agent) is not None

    def container_running(self, agent: str) -> bool:
        """Check if agent container is running"""
        container = self.get_container(agent)
        return container is not None and container.status == "running"

    def launch_agent(self, agent: str, wait_healthy: bool = True) -> bool:
        """Launch agent container using Docker Compose"""
        if agent not in self.agents:
            self.log(f"Unknown agent: {agent}", "ERROR")
            return False

        # Check if already running
        if self.container_running(agent):
            self.log(f"{agent} agent is already running", "WARNING")
            return True

        compose_file = self.agents[agent]["compose_file"]
        compose_path = self.project_root / compose_file

        if not compose_path.exists():
            self.log(f"Docker Compose file not found: {compose_path}", "ERROR")
            return False

        self.log(f"Launching {agent} agent...", "INFO")

        try:
            # Use docker-compose to launch
            import subprocess

            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    str(compose_path),
                    "-p",
                    f"vllm-{agent}",
                    "up",
                    "-d",
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.log(f"Failed to launch {agent}: {result.stderr}", "ERROR")
                return False

            self.log(f"{agent} agent launched", "SUCCESS")

            # Wait for container to be healthy
            if wait_healthy:
                self.log(f"Waiting for {agent} agent to be healthy...", "INFO")
                if self.wait_container_healthy(agent, timeout=120):
                    self.log(f"{agent} agent is ready", "SUCCESS")
                    self.save_state(agent)
                    return True
                else:
                    self.log(f"{agent} agent failed health check", "WARNING")
                    return False

            self.save_state(agent)
            return True

        except Exception as e:
            self.log(f"Error launching {agent}: {str(e)}", "ERROR")
            return False

    def stop_agent(self, agent: str, force: bool = False) -> bool:
        """Stop agent container"""
        if agent not in self.agents:
            self.log(f"Unknown agent: {agent}", "ERROR")
            return False

        container = self.get_container(agent)
        if container is None:
            self.log(f"{agent} agent is not running", "INFO")
            return True

        self.log(f"Stopping {agent} agent...", "INFO")

        try:
            if force or container.status == "running":
                container.stop(timeout=10)
                self.log(f"{agent} agent stopped", "SUCCESS")
                return True
            else:
                self.log(f"{agent} agent is not running (status: {container.status})", "INFO")
                return True
        except Exception as e:
            self.log(f"Error stopping {agent}: {str(e)}", "ERROR")
            return False

    def stop_all_agents(self) -> None:
        """Stop all running agents"""
        for agent in self.agents:
            if self.container_running(agent):
                self.stop_agent(agent)

    def switch_agent(self, new_agent: str) -> bool:
        """Switch to a new agent (stop current, launch new)"""
        if new_agent not in self.agents:
            self.log(f"Unknown agent: {new_agent}", "ERROR")
            return False

        current_agent = self.load_state()

        if current_agent and current_agent != new_agent:
            self.log(f"Stopping {current_agent} agent...", "INFO")
            self.stop_agent(current_agent)
            time.sleep(2)  # Wait for cleanup

        return self.launch_agent(new_agent)

    def get_status(self) -> None:
        """Display status of all agents"""
        print("\n📊 Agent Status:\n")

        for agent_name, config in self.agents.items():
            container = self.get_container(agent_name)
            status_emoji = "🟢" if self.container_running(agent_name) else "🔴"
            status_text = "RUNNING" if self.container_running(agent_name) else "STOPPED"

            print(f"{status_emoji} {agent_name.upper():12} {status_text:10} (Port: {config['port']})")

            if container:
                print(f"   Container: {container.short_id}")
                print(f"   Memory: {config['gpu_memory']}")

        current = self.load_state()
        if current:
            print(f"\n   Current Agent: {current.upper()}")

        print()

    def get_logs(self, agent: str, lines: int = 100) -> None:
        """Display agent logs"""
        if agent not in self.agents:
            self.log(f"Unknown agent: {agent}", "ERROR")
            return

        container = self.get_container(agent)
        if container is None:
            self.log(f"{agent} agent container not found", "ERROR")
            return

        self.log(f"Last {lines} log lines for {agent} agent:", "INFO")
        print()

        try:
            logs = container.logs(tail=lines, stream=False)
            print(logs.decode("utf-8"))
        except Exception as e:
            self.log(f"Error retrieving logs: {str(e)}", "ERROR")

    def gpu_stats(self) -> None:
        """Display GPU memory usage"""
        self.log("GPU Memory Usage:", "INFO")

        try:
            import subprocess

            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(result.stdout)
            else:
                self.log("nvidia-smi not available", "WARNING")

        except Exception as e:
            self.log(f"Error retrieving GPU stats: {str(e)}", "ERROR")

    def wait_container_healthy(self, agent: str, timeout: int = 120) -> bool:
        """Wait for container to report healthy status"""
        container = self.get_container(agent)
        if container is None:
            return False

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                container.reload()
                if container.health_status == "healthy":
                    return True
            except Exception:
                pass

            time.sleep(2)

        return False

    def test_api(self, agent: str) -> bool:
        """Test agent API endpoint"""
        if agent not in self.agents:
            self.log(f"Unknown agent: {agent}", "ERROR")
            return False

        port = self.agents[agent]["port"]
        url = f"http://localhost:{port}/v1/models"

        try:
            import requests

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.log(f"{agent} agent API is responding", "SUCCESS")
                return True
            else:
                self.log(f"{agent} agent API returned {response.status_code}", "ERROR")
                return False
        except requests.exceptions.ConnectionError:
            self.log(f"Cannot connect to {agent} agent on port {port}", "ERROR")
            return False
        except Exception as e:
            self.log(f"API test error: {str(e)}", "ERROR")
            return False

    def main(self, args: argparse.Namespace) -> int:
        """Main entry point"""
        print("\n🚀 VLLM Agent Manager\n")

        if args.list:
            self.list_agents()
            return 0

        if args.launch:
            if self.launch_agent(args.launch):
                return 0
            else:
                return 1

        if args.stop:
            if self.stop_agent(args.stop):
                return 0
            else:
                return 1

        if args.stop_all:
            self.stop_all_agents()
            return 0

        if args.switch:
            if self.switch_agent(args.switch):
                return 0
            else:
                return 1

        if args.status:
            self.get_status()
            return 0

        if args.logs:
            self.get_logs(args.logs, args.log_lines)
            return 0

        if args.gpu_stats:
            self.gpu_stats()
            return 0

        if args.test_api:
            if self.test_api(args.test_api):
                return 0
            else:
                return 1

        if args.current:
            current = self.load_state()
            if current:
                print(f"Current agent: {current.upper()}")
            else:
                print("No agent currently active")
            return 0

        # Show help if no args
        if len(sys.argv) == 1:
            print("Run with --help for usage information")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="VLLM Multi-Agent Docker Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch an agent
  python3 agent_manager.py --launch architect

  # Switch to a different agent
  python3 agent_manager.py --switch dev

  # Check status
  python3 agent_manager.py --status

  # View logs
  python3 agent_manager.py --logs dev

  # GPU memory usage
  python3 agent_manager.py --gpu-stats

  # Stop all agents
  python3 agent_manager.py --stop-all
        """,
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available agents",
    )
    parser.add_argument(
        "--launch",
        type=str,
        help="Launch specific agent (architect, dev, po)",
    )
    parser.add_argument(
        "--stop",
        type=str,
        help="Stop specific agent",
    )
    parser.add_argument(
        "--stop-all",
        action="store_true",
        help="Stop all running agents",
    )
    parser.add_argument(
        "--switch",
        type=str,
        help="Switch to different agent (stops current, launches new)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display status of all agents",
    )
    parser.add_argument(
        "--current",
        action="store_true",
        help="Show currently active agent",
    )
    parser.add_argument(
        "--logs",
        type=str,
        help="Display logs for agent",
    )
    parser.add_argument(
        "--log-lines",
        type=int,
        default=100,
        help="Number of log lines to display (default: 100)",
    )
    parser.add_argument(
        "--gpu-stats",
        action="store_true",
        help="Display GPU memory usage",
    )
    parser.add_argument(
        "--test-api",
        type=str,
        help="Test API endpoint for agent",
    )

    args = parser.parse_args()
    manager = AgentManager()
    sys.exit(manager.main(args))


if __name__ == "__main__":
    main()
