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

- 🧩 **15 Specialized AI Personas** (Architecture, Dev, Test, Review, Debug, Planning, Orchestration)
- ⚙️ **Automated Setup** from Modelfiles (100% reproducible)
- ✅ **Built‑in Validation** and health checks
- 🧪 **Agent Testing** with performance metrics
- 💻 **GPU Optimized** (RTX 5060‑Ti, 4070, A2000, etc.)
- 🔐 **100% Local** — no cloud dependency
- 🌐 **Cross‑platform** (Linux, macOS, Windows)
- 🧱 **Extensible** — easily add your own personas

### 📦 What's New (October 2025)

✅ **Refactored Setup Script:**
- Agent names automatically extracted from Modelfiles
- Strict validation of Modelfile tags
- Cleaner PERSONAS dictionary (metadata only)

✅ **All Modelfiles Updated:**
- Generic tags for reliability (`qwen2.5:32b-instruct` instead of `-q5_K_M`)
- Fixed typos and invalid model references
- 7 unique base models (down from 11+)

📚 **Documentation:**
- [`MODELFILE_TAGS.md`](docs/MODELFILE_TAGS.md) - Complete tag reference

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
python3 setup_ollama.py --global-env --threads 8
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

## 🧩 Available Personas

This setup includes **15 specialized AI agents** organized by function:

### 🏗️ Architecture Agents (5 variants)

| Persona ID | Agent Name | Base Model | Role |
|------------|------------|------------|------|
| **arch** | `arch-agent` | `qwen2.5:32b-instruct` | Principal architect - DDD, microservices, cloud-native |
| **arch-deepseek** | `arch-agent-deepseek` | `deepseek-r1:32b` | Architecture with chain-of-thought reasoning |
| **arch-qwen3_14b** | `arch-agent-qwen3_14b` | `qqwen3:14b` | Mid-size architecture decisions |
| **arch-qwen3_30b** | `arch-agent-qwen3_30b` | `qwen3:30b` | Large-scale architecture reasoning |
| **arch-qwen3_coder** | `arch-agent-qwen3_coder` | `qwen3-coder:30b` | Code-focused architecture |

### 💻 Development Agents (2 variants)

| Persona ID | Agent Name | Base Model | Role |
|------------|------------|------------|------|
| **dev** | `dev-agent` | `qwen2.5-coder:32b` | Full-stack development, SOLID principles |
| **dev-qw3** | `dev-agent-qw3` | `qwen3-coder:30b` | Development with latest Qwen3 coder |

### 🧪 Quality Assurance Agents (4 agents)

| Persona ID | Agent Name | Base Model | Role |
|------------|------------|------------|------|
| **test** | `test-agent` | `qwen2.5-coder:14b-instruct` | Test generation (unit, integration, e2e) |
| **review** | `review-agent` | `qwen2.5-coder:14b-instruct` | Code review, security, performance |
| **debug** | `debug-agent` | `qwen2.5-coder:32b-instruct` | Debugging and error analysis |
| **refactor** | `refactor-agent` | `qwen2.5-coder:14b-instruct` | Code refactoring, design patterns |

### 📋 Planning & Documentation Agents (4 agents)

| Persona ID | Agent Name | Base Model | Role |
|------------|------------|------------|------|
| **plan** | `plan-agent` | `qwen2.5:14b-instruct` | Detailed project planning with DevOps |
| **planlite** | `planlite-agent` | `qwen2.5:7b-instruct` | Quick sprint and task planning |
| **orch** | `orch-agent` | `qwen2.5:3b-instruct` | Fast orchestration and routing |
| **docs** | `docs-agent` | `qwen2.5:7b-instruct` | API docs, diagrams, user guides |

### Usage Examples

```bash
# Create specific agents
python3 setup_ollama.py --pull --create --persona arch,dev,test

# Run agents
ollama run arch-agent "Design a microservices architecture for e-commerce"
ollama run dev-agent "Implement authentication with JWT in ASP.NET Core"
ollama run test-agent "Generate tests for the authentication controller"

# Use variants
ollama run arch-agent-deepseek "Complex system design with reasoning chain"
ollama run dev-agent-qw3 "Latest coding model for modern frameworks"
```

---

## 📚 Additional Documentation

For more details on architecture agent variants and their use cases:

- **Architecture Agents Guide**: [`docs/ARCH_AGENT_VARIANTS_GUIDE.md`](docs/ARCH_AGENT_VARIANTS_GUIDE.md)
- **Model Selection Guide**: [`docs/MODEL_CHOICES.md`](docs/MODEL_CHOICES.md)
- **Parameter Optimization**: [`docs/PARAMETER_OPTIMIZATION_SUMMARY.md`](docs/PARAMETER_OPTIMIZATION_SUMMARY.md)
- **System Prompts Reference**: [`docs/SYSTEM_PROMPTS.md`](docs/SYSTEM_PROMPTS.md)

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
2. Recreate the persona: `python3 setup_ollama.py --create --persona dev`
3. Test: `ollama run dev-agent "your test prompt"`

---

## 💡 Why Local-First?

| Benefit              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| 🔐 **Privacy**        | Keep all code and context local — ideal for internal projects |
| ⚡ **Performance**    | Optimized for 16 GB VRAM GPUs with efficient model selection |
| 🧩 **Specialization** | Each persona is tuned for a distinct development role        |
| 🧱 **Simplicity**     | One Python script — no Docker, no cloud dependencies         |
| 🧠 **Extensible**     | Add your own personas or change base models easily           |

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

- 🧠 **Ollama** - Local LLM runtime
- ⚙️ **Qwen 2.5** & **Qwen3** - High-quality coding models
- 🤖 **DeepSeek R1** - Advanced reasoning capabilities
- 💻 Clean, private, local AI for everyday coding & architecture
- 💻 Clean, private, local AI for everyday coding & architecture

<p align
