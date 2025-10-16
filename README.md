# 🧠 Ollama Dev‑First Setup

<p align="center">
  <b>Local‑Only AI Environment for Developers</b><br>
  <sub>Configure, orchestrate, and run specialized Ollama personas for software development — fully local, GPU‑optimized, and private.</sub>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-green.svg">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue">
  <img src="https://img.shields.io/badge/Ollama-compatible-orange">
</p>


---

## 🚀 Overview

This project provides `setup_ollama.py` — a complete setup and validation tool for **Ollama** development environments.  
It applies **global environment variables** (systemd root‑level), creates domain‑specific AI personas, and validates your installation.

### ✅ Highlights

- 🧩 Persona‑based AI agents (Dev, Arch, Test, Plan, Orchestrator)
- ⚙️ Global configuration (root/systemd override or user fallback)
- ✅ Built‑in validation and health checks
- 🧪 Agent testing with performance metrics
- 💻 Optimized for GPUs (e.g., RTX 4060‑Ti, 4070, A2000)
- 🔐 100% Local — no cloud dependency
- 🌐 Cross‑platform (Linux, macOS, Windows)
- 🧱 Extensible — easily add your own personas

---

## 🧰 Installation & Usage

### 🧾 1. Set Global Environment (systemd root mode)

If Ollama runs as a system service (installed via `.deb` or `.rpm`):

```bash
sudo python3 setup_ollama.py --global-env --threads 14
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

**What this does:**

- Creates `/etc/systemd/system/ollama.service.d/override.conf`

- Applies optimal environment variables:

  ```
  OLLAMA_NUM_GPU=1
  OLLAMA_GPU_LAYERS=999
  OLLAMA_NUM_THREADS=8
  OLLAMA_MAX_LOADED_MODELS=1
  OLLAMA_KEEP_ALIVE=5m
  CUDA_VISIBLE_DEVICES=0
  OLLAMA_FLASH_ATTENTION=1
  OLLAMA_MAX_QUEUE=512
  ```

<details>
<summary><b>💡 Without sudo (user fallback)</b></summary>


```bash
python3 setup_ollama_local.py --global-env --threads 8
systemctl --user daemon-reload && systemctl --user restart ollama
```

</details>

---

### 👤 2. Create Personas On Demand

List available personas:

```bash
python3 setup_ollama.py --list
```

Pull and create specific personas (example):

```bash
python3 setup_ollama.py --pull --create --persona dev,arch
```

Once created, you can run them instantly:

```bash
ollama run dev-agent
ollama run arch-agent
```

---

### ✅ 3. Validate Setup

Check if everything is properly installed:

```bash
# Full validation (includes agent tests)
python3 setup_ollama.py --validate

# Quick validation (skip agent tests)
python3 setup_ollama.py --validate --quick

# Test specific agent
python3 setup_ollama.py --test-agent arch-agent

# Check VRAM usage
python3 setup_ollama.py --check-vram
```

**Validation includes:**
- ✅ Ollama installation check
- ✅ Base models verification
- ✅ Agent creation status
- ✅ VRAM usage monitoring
- ✅ Agent response tests (optional)
- ✅ Performance metrics

---

## 🧩 Personas & Their Roles

| Persona               | Base Model                            | Role                          | Context | Why It's Useful                                         |
| --------------------- | ------------------------------------- | ----------------------------- | ------- | ------------------------------------------------------- |
| 🧑‍💻 **dev-agent**      | `qwen2.5-coder:32b-instruct-q4_K_M`   | Code generation & refactoring | 32K     | Larger model for complex .NET codebases, SOLID, optimization |
| 💻 **dev-qwen3coder** ⭐ | `qwen3-coder:30b-q5_K_M`              | Code gen (2025 model)         | 32K     | Latest Qwen3-Coder - +8% quality, better debugging (-15% bugs) |
| 🏗️ **arch-agent**      | `qwen2.5:32b-instruct-q5_K_M`         | Architecture & design         | 32K     | Deep reasoning for DDD, CQRS, microservices, K8s patterns |
| 🚀 **arch-qwen3** ⭐    | `qwen3:32b-instruct-q5_K_M`           | Architecture (2025 model)     | 32K     | Latest Qwen3 - improved reasoning, code & math (+5% better) |
| ⚡ **arch-qwen3moe**    | `qwen3:30b-q5_K_M` (MoE)              | Architecture (fast)           | 32K     | 50% faster, 12GB VRAM - ideal for interactive sessions |
| 🧠 **arch-deepseek**   | `deepseek-r1:32b-q4_K_M`              | Architecture (reasoning)      | 32K     | Chain-of-thought native - best for complex problems |
| 🧪 **test-agent**      | `qwen2.5-coder:14b-instruct-q5_K_M`   | Testing & QA                  | 16K     | Comprehensive test generation (unit, integration, e2e) |
| 🗂️ **plan-agent**      | `qwen2.5:14b-instruct-q5_K_M`         | Spec‑driven planning          | 32K     | Detailed specs with DevOps and deployment considerations |
| ⚡ **plan‑lite‑agent** | `qwen2.5:7b-instruct-q5_K_M`          | Quick sprint planning         | 8K      | Fast agile planning for sprints and tasks |
| 🔀 **orch-agent**      | `qwen2.5:3b-instruct-q5_K_M`          | Orchestration                 | 4K      | Fast routing to appropriate personas |
| �️ **review-agent**    | `qwen2.5-coder:14b-instruct-q5_K_M`   | Code review                   | 32K     | Security, performance, and maintainability analysis |
| 🐛 **debug-agent**     | `qwen2.5-coder:32b-instruct-q4_K_M`   | Debugging specialist          | 32K     | Deep analysis of errors, stack traces, and root causes |
| ♻️ **refactor-agent**  | `qwen2.5-coder:14b-instruct-q5_K_M`   | Code refactoring              | 32K     | Design patterns, complexity reduction, code smell fixes |
| 📝 **docs-agent**      | `qwen2.5:7b-instruct-q5_K_M`          | Documentation                 | 16K     | API docs, architecture diagrams, user guides |

---

## 🆕 New Models 2025

Four new agent variants are available using the latest 2025 models:

### Development Agent (Qwen3-Coder)

```bash
# Latest coding model: Qwen3-Coder (recommended for dev work)
python3 setup_ollama_local.py --persona dev-qwen3coder --pull --create
ollama run dev-agent-qwen3coder
```

**Improvements over Qwen2.5-Coder:**
- +8% code quality across all languages
- +12% better bug detection
- -15% fewer code hallucinations
- Up-to-date with 2025 frameworks

**See detailed guide:** [`docs/DEV_AGENT_QWEN3CODER_GUIDE.md`](docs/DEV_AGENT_QWEN3CODER_GUIDE.md)

### Architecture Agents

```bash
# Recommended: Qwen3 (balanced, best overall)
python3 setup_ollama_local.py --persona arch-qwen3 --pull --create
ollama run arch-agent-qwen3

# Fast: Qwen3 MoE (50% faster, uses 12GB VRAM)
python3 setup_ollama_local.py --persona arch-qwen3moe --pull --create
ollama run arch-agent-qwen3moe

# Best reasoning: DeepSeek-R1 (chain-of-thought native)
python3 setup_ollama_local.py --persona arch-deepseek --pull --create
ollama run arch-agent-deepseek
```

**See detailed comparison:** [`docs/LATEST_MODELS_2025.md`](docs/LATEST_MODELS_2025.md)  
**See usage guide:** [`docs/ARCH_AGENT_VARIANTS_GUIDE.md`](docs/ARCH_AGENT_VARIANTS_GUIDE.md)

---

## 📦 Modelfile Structure

Each persona is defined by a **Modelfile** in the `modelfiles/` directory. This approach offers several advantages:

- **Maintainability**: System prompts are stored in separate, version-controlled files
- **Readability**: Multi-line prompts with proper formatting
- **Reusability**: Can be shared, modified, or reused across projects
- **No syntax issues**: Avoids inline string formatting problems

### Example Modelfile Structure

```dockerfile
FROM qwen2.5-coder:32b-instruct-q4_K_M

SYSTEM """You are an expert software engineer...
[Multi-line system prompt with proper formatting]
"""

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx 32768
```

### Customizing Personas

To modify a persona's behavior:
1. Edit the corresponding Modelfile in `modelfiles/[persona]-agent.Modelfile`
2. Recreate the persona: `python3 setup_ollama_local.py --create --persona dev`
3. Test: `ollama run dev-agent "your test prompt"`

---

## �💡 Why Local‑First?

| Benefit              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| 🔐 **Privacy**        | Keep all code and context local — ideal for internal projects |
| ⚡ **Performance**    | Quantized models (`q4`, `q5`) fit well in 16 GB VRAM GPUs    |
| 🧩 **Specialization** | Each persona is tuned for a distinct dev role                |
| 🧱 **Simplicity**     | One Python script — no Docker, no cloud                      |
| 🧠 **Extensible**     | Add your own personas or change base models easily           |

---

---

## 🔄 Recommended Workflow

Since you're using **one model at a time**, here's an optimized development workflow:

### 📋 Project Planning Phase
```bash
ollama run orch-agent "I need to plan a new microservice for user authentication"
# Routes to → plan-agent or plan-lite-agent
```

### 💻 Development Phase
```bash
ollama run dev-agent "Implement JWT authentication with refresh tokens in ASP.NET Core"
```

### 👁️ Code Review Phase
```bash
ollama run review-agent "Review this authentication controller for security issues: [paste code]"
```

### 🧪 Testing Phase
```bash
ollama run test-agent "Generate comprehensive tests for the AuthController including edge cases"
```

### 🐛 Debugging Phase
```bash
ollama run debug-agent "Analyze this stack trace: [paste error]"
```

### 🏗️ Architecture Decisions
```bash
ollama run arch-agent "Should I use CQRS for this microservice? Evaluate trade-offs"
```

### ♻️ Refactoring Phase
```bash
ollama run refactor-agent "Refactor this service to follow Repository pattern"
```

### 📝 Documentation Phase
```bash
ollama run docs-agent "Generate API documentation for the authentication endpoints"
```

---

## ⚡ Performance Tips

| Tip | Description | Impact |
|-----|-------------|--------|
| 🚀 **Pre-load models** | Run `ollama pull <model>` before first use | Faster first response |
| 💾 **Keep models cached** | Frequently used models stay in memory (5min) | No reload latency |
| 🧹 **Unload when switching** | Use `ollama stop <model>` to free VRAM | Faster context switch |
| 📊 **Monitor VRAM** | Use `nvidia-smi -l 1` to watch GPU usage | Prevent OOM |
| 🧠 **Use appropriate persona** | Smaller models (3B-7B) for simple tasks | Save VRAM & CPU |
| 🔧 **Adjust threads** | Increase `--threads` if not using IDEs | Better CPU utilization |

---

## 🖥️ Requirements

| Requirement    | Recommended                              | Notes                                      |
| -------------- | ---------------------------------------- | ------------------------------------------ |
| Ollama version | ≥ 0.3.8                                  | Latest stable recommended                  |
| GPU            | 16 GB VRAM (RTX 4060 Ti, 4070, A2000)    | Tested on RTX 4060 Ti 16GB                 |
| CPU            | 8+ cores (Ryzen 7 5700X or equivalent)   | 8 threads reserved for Ollama              |
| RAM            | ≥ 32 GB (64 GB recommended)              | For hybrid GPU+CPU offload with 32B models |
| OS             | Linux (systemd), macOS, or Windows 11    | Flash Attention requires CUDA ≥ 8.0        |

> **⚠️ Important**: If running IDEs + Docker + K8s simultaneously, ensure adequate CPU/RAM headroom.

---

## ⚙️ For Windows Users

- Environment variables are applied using `setx` and added to:

  ```
  ~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1
  ```

- Restart PowerShell or log out/in to apply.

---

## 🧩 Troubleshooting

| Issue                   | Fix                                                 |
| ----------------------- | --------------------------------------------------- |
| Ollama ignores env vars | Run as `sudo` so env applies to systemd root.       |
| Not enough VRAM         | Use `plan‑lite‑agent` or reduce `--num_gpu_layers`. |
| “Model not found”       | Run `--pull` before `--create`.                     |
| Ollama service error    | Run `sudo systemctl status ollama` to debug.        |

---

## 🛠️ Contributing

Feel free to:

- 🧩 Add new personas for specific languages or domains  
- ⚙️ Improve model presets or default parameters  
- 📦 Submit PRs for cross‑platform optimizations

---

## 📜 License

Licensed under the **MIT License** — free for personal and commercial use.

---

## ❤️ Credits

Built for developers who love:

- 🧠 **Ollama**
- ⚙️ **Qwen 2.5**, **DeepSeek R1**, **Llama 3.1**
- 💻 Clean, private, local AI for everyday coding & architecture

<p align="center"><b>Happy Building 🚀</b></p>
