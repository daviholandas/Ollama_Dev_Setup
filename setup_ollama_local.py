#!/usr/bin/env python3
# setup_ollama_local_v3.py
# Local-only Ollama setup for software development.
# - Global env via systemd **root** override (if run with sudo)
# - Fallback to user-level shell profiles + systemd --user (if no sudo)
# - On-demand model creation with --persona (dev, arch, test, plan, planlite, orch)
# - Cross-platform best-effort (Windows: sets user env via `setx` and PowerShell profile)
#
# Examples:
#   sudo python3 setup_ollama_local_v3.py --global-env --threads 14
#   sudo systemctl daemon-reload && sudo systemctl restart ollama
#   python3 setup_ollama_local_v3.py --pull --create --persona dev,plan
#   python3 setup_ollama_local_v3.py --list

import argparse, os, sys, subprocess, tempfile, platform
from pathlib import Path

PERSONAS = {
  "dev": {
    "agent": "dev-agent",
    "from": "qwen2.5-coder:14b-instruct-q5_K_M",
    "system": ("You are a senior software engineer with deep expertise in software development fundamentals and principles. "
               "Mastery of the .NET ecosystem (C#, ASP.NET Core, EF Core). Focus on clean code, SOLID, design patterns, "
               "data structures, algorithms, and performance optimization. Provide complete, well-tested, production-ready code."),
    "params": {
      "temperature": "0.2", "top_p": "0.9", "top_k": "40",
      "repeat_penalty": "1.1", "num_ctx": "8192", "num_predict": "1024",
      "num_gpu_layers": "999", "stop": "```"
    }
  },
  "arch": {
    "agent": "arch-agent",
    "from": "deepseek-r1:14b-qwen-distill-q5_K_M",
    "system": ("You are a principal software architect. Apply first-principles reasoning, evaluate trade-offs (CAP, consistency, coupling/cohesion), "
               "and recommend solutions fitting constraints and business context."),
    "params": {
      "temperature": "0.5", "top_p": "0.9", "top_k": "50",
      "repeat_penalty": "1.05", "num_ctx": "8192", "num_predict": "1024",
      "num_gpu_layers": "999"
    }
  },
  "test": {
    "agent": "test-agent",
    "from": "qwen2.5-coder:14b-instruct-q5_K_M",
    "system": ("You are a QA specialist for .NET projects (xUnit/NUnit/MSTest). Create comprehensive test suites: happy paths, edges, boundaries, "
               "errors, concurrency, security. Keep tests maintainable."),
    "params": {
      "temperature": "0.15", "top_p": "0.9", "top_k": "32",
      "repeat_penalty": "1.08", "num_ctx": "4096", "num_predict": "768",
      "num_gpu_layers": "999", "stop": "```"
    }
  },
  "plan": {
    "agent": "plan-agent",
    "from": "qwen2.5:14b-instruct-q4_K_M",
    "system": ("You are a planning specialist for spec-driven software development. Output: scope, assumptions, functional & non-functional requirements, "
               "acceptance criteria (Given-When-Then), risks, dependencies, milestones, and a prioritized task breakdown (with DoD). Be concise and executable."),
    "params": {
      "temperature": "0.5", "top_p": "0.95", "top_k": "50",
      "repeat_penalty": "1.05", "num_ctx": "8192", "num_predict": "1536",
      "num_gpu_layers": "999"
    }
  },
  "planlite": {
    "agent": "plan-lite-agent",
    "from": "qwen2.5:7b-instruct-q5_K_M",
    "system": ("You are a lightweight planning agent. Produce short actionable specs: scope, key requirements, concise acceptance criteria, prioritized checklist."),
    "params": {
      "temperature": "0.4", "top_p": "0.95", "top_k": "50",
      "repeat_penalty": "1.07", "num_ctx": "4096", "num_predict": "1024",
      "num_gpu_layers": "999"
    }
  },
  "orch": {
    "agent": "orch-agent",
    "from": "llama3.1:8b-instruct-q4_0",
    "system": ("You are a lightweight orchestrator for dev tasks. Route requests to the right persona and keep reasoning brief."),
    "params": {
      "temperature": "0.3", "top_p": "0.9", "top_k": "40",
      "repeat_penalty": "1.1", "num_ctx": "1024", "num_predict": "256",
      "num_gpu_layers": "0"
    }
  }
}

DEFAULT_ENVS = {
  "OLLAMA_NUM_GPU": "1",
  "OLLAMA_GPU_LAYERS": "999",
  "OLLAMA_NUM_THREADS": "12",
  "OLLAMA_MAX_LOADED_MODELS": "1",
  "OLLAMA_KEEP_ALIVE": "10m",
  "CUDA_VISIBLE_DEVICES": "0",
  "OLLAMA_FLASH_ATTENTION": "1"
}

def have_ollama() -> bool:
  try:
    subprocess.run(["ollama","--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return True
  except Exception:
    return False

def run(cmd):
  print("$", " ".join(cmd))
  subprocess.run(cmd, check=True)

def write_system_override(envs):
  override_dir = Path("/etc/systemd/system/ollama.service.d")
  override_dir.mkdir(parents=True, exist_ok=True)
  override = override_dir / "override.conf"
  lines = ["[Service]"] + [f'Environment="{k}={v}"' for k, v in envs.items()]
  override.write_text("\n".join(lines) + "\n", encoding="utf-8")
  print(f"Wrote systemd override: {override}")
  print("Now run: sudo systemctl daemon-reload && sudo systemctl restart ollama")

def write_user_profiles(envs):
  home = Path.home()
  targets = [home / ".bashrc", home / ".zshrc", home / ".profile"]
  for t in targets:
    try:
      with open(t, "a", encoding="utf-8") as f:
        for k, v in envs.items():
          f.write(f"export {k}='{v}'\n")
      print(f"Appended envs to: {t}")
    except Exception as e:
      print(f"WARNING: could not append to {t}: {e}")
  try:
    override_dir = home / ".config/systemd/user/ollama.service.d"
    override_dir.mkdir(parents=True, exist_ok=True)
    override = override_dir / "override.conf"
    lines = ["[Service]"] + [f"Environment={k}={v}" for k,v in envs.items()]
    override.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote user systemd override: {override}")
    print("Apply with: systemctl --user daemon-reload && systemctl --user restart ollama")
  except Exception as e:
    print(f"NOTE: systemd user override not created: {e}")

def write_windows_envs(envs):
  os.environ.update(envs)
  for k, v in envs.items():
    try:
      run(["setx", k, str(v)])
    except Exception as e:
      print(f"WARNING: setx failed for {k}: {e}")
  profile = os.path.expanduser("~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1")
  Path(profile).parent.mkdir(parents=True, exist_ok=True)
  with open(profile, "a", encoding="utf-8") as f:
    for k, v in envs.items():
      f.write(f"$env:{k}='{v}'\n")
  print(f"PowerShell profile updated: {profile}")

def write_global_envs(envs, threads):
  envs = envs.copy()
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

def make_modelfile_text(frm: str, system: str, params: dict) -> str:
  lines = [f"FROM {frm}", f"SYSTEM {system}"]
  for k, v in params.items():
    if isinstance(v, str) and ((" " in v) or v == "```"):
      lines.append(f'PARAMETER {k} "{v}"')
    else:
      lines.append(f"PARAMETER {k} {v}")
  return "\n".join(lines) + "\n"

def create_persona(persona: str, do_pull: bool, do_create: bool):
  cfg = PERSONAS[persona]
  if do_pull:
    run(["ollama", "pull", cfg["from"]])
  if do_create:
    txt = make_modelfile_text(cfg["from"], cfg["system"], cfg["params"])
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".Modelfile", encoding="utf-8") as tf:
      tf.write(txt)
      temp_path = tf.name
    try:
      run(["ollama", "create", cfg["agent"], "-f", temp_path])
    finally:
      try:
        Path(temp_path).unlink(missing_ok=True)
      except Exception:
        pass

def main():
  ap = argparse.ArgumentParser(description="Local-only Ollama setup (systemd root env + on-demand personas).")
  ap.add_argument("--global-env", action="store_true", help="Persist global env vars for systemd/root or user fallback")
  ap.add_argument("--threads", type=int, default=int(DEFAULT_ENVS["OLLAMA_NUM_THREADS"]), help="Value for OLLAMA_NUM_THREADS")
  ap.add_argument("--persona", help="Comma-separated personas to create: dev,arch,test,plan,planlite,orch")
  ap.add_argument("--pull", action="store_true", help="Run `ollama pull` for required base models")
  ap.add_argument("--create", action="store_true", help="Run `ollama create` for specified personas")
  ap.add_argument("--list", action="store_true", help="List available personas and exit")
  args = ap.parse_args()

  if args.list:
    print("Available personas: " + ", ".join(PERSONAS.keys()))
    sys.exit(0)

  if args.global_env:
    write_global_envs(DEFAULT_ENVS, args.threads)

  if args.persona:
    if not have_ollama():
      print("ERROR: 'ollama' not found in PATH. Install Ollama first.")
      sys.exit(1)
    requested = [p.strip().lower() for p in args.persona.split(",") if p.strip()]
    invalid = [p for p in requested if p not in PERSONAS]
    if invalid:
      print("Invalid personas: " + ", ".join(invalid))
      print("Available personas: " + ", ".join(PERSONAS.keys()))
      sys.exit(2)
    for p in requested:
      create_persona(p, args.pull, args.create)

  if not (args.global_env or args.persona):
    print("Nothing to do. Use --global-env and/or --persona. Try --list.")

if __name__ == "__main__":
  try:
    main()
  except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
  except KeyboardInterrupt:
    sys.exit(130)
