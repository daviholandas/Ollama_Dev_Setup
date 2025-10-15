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

This script (`setup_ollama_local.py`) automatically configures **Ollama** for a complete, local‑first software development experience.  
It applies **global environment variables** (systemd root‑level) and allows **on‑demand creation** of domain‑specific AI personas.

### ✅ Highlights

- 🧩 Persona‑based AI agents (Dev, Arch, Test, Plan, Orchestrator)
- ⚙️ Global configuration (root/systemd override or user fallback)
- 💻 Optimized for GPUs (e.g., RTX 4060‑Ti, 4070, A2000)
- 🔐 100% Local — no cloud dependency
- 🧱 Extensible — easily add your own personas

---

## 🧰 Installation & Usage

### 🧾 1. Set Global Environment (systemd root mode)

If Ollama runs as a system service (installed via `.deb` or `.rpm`):

```bash
sudo python3 setup_ollama_local.py --global-env --threads 12
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

**What this does:**

- Creates `/etc/systemd/system/ollama.service.d/override.conf`

- Applies optimal environment variables:

  ```
  OLLAMA_NUM_GPU=1
  OLLAMA_GPU_LAYERS=999
  OLLAMA_NUM_THREADS=12
  OLLAMA_MAX_LOADED_MODELS=1
  OLLAMA_KEEP_ALIVE=10m
  CUDA_VISIBLE_DEVICES=0
  OLLAMA_FLASH_ATTENTION=1
  ```

<details>
<summary><b>💡 Without sudo (user fallback)</b></summary>


```bash
python3 setup_ollama_local.py --global-env --threads 12
systemctl --user daemon-reload && systemctl --user restart ollama
```

</details>

---

### 👤 2. Create Personas On Demand

List available personas:

```bash
python3 setup_ollama_local.py --list
```

Pull and create specific personas (example):

```bash
python3 setup_ollama_local.py --pull --create --persona dev,plan
```

Once created, you can run them instantly:

```bash
ollama run dev-agent
ollama run plan-agent
ollama run orch-agent  # CPU-only
```

---

## 🧩 Personas & Their Roles

| Persona               | Base Model                            | Role                          | Why It’s Useful                                         |
| --------------------- | ------------------------------------- | ----------------------------- | ------------------------------------------------------- |
| 🧑‍💻 **dev-agent**      | `qwen2.5-coder:14b-instruct-q5_K_M`   | Code generation & refactoring | Expert in .NET, clean code, SOLID, and optimization     |
| 🏗️ **arch-agent**      | `deepseek-r1:14b-qwen-distill-q5_K_M` | Architecture & design         | High reasoning depth, DDD, CQRS, scalability trade‑offs |
| 🧪 **test-agent**      | `qwen2.5-coder:14b-instruct-q5_K_M`   | Testing & QA                  | Generates maintainable tests, detects edge cases        |
| 🗂️ **plan-agent**      | `qwen2.5:14b-instruct-q4_K_M`         | Spec‑driven planning          | Produces detailed specs and milestones                  |
| ⚡ **plan‑lite‑agent** | `qwen2.5:7b-instruct-q5_K_M`          | Quick sprint planning         | Lightweight, fast for agile breakdowns                  |
| 🔀 **orch-agent**      | `llama3.1:8b-instruct-q4_0`           | Orchestration                 | CPU‑only router that coordinates all other agents       |

---

## 💡 Why Local‑First?

| Benefit              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| 🔐 **Privacy**        | Keep all code and context local — ideal for internal projects |
| ⚡ **Performance**    | Quantized models (`q4`, `q5`) fit well in 16 GB VRAM GPUs    |
| 🧩 **Specialization** | Each persona is tuned for a distinct dev role                |
| 🧱 **Simplicity**     | One Python script — no Docker, no cloud                      |
| 🧠 **Extensible**     | Add your own personas or change base models easily           |

---

## 🖥️ Requirements

| Requirement    | Recommended                           |
| -------------- | ------------------------------------- |
| Ollama version | ≥ 0.3.8                               |
| GPU            | 16 GB VRAM (RTX 4060 Ti, 4070, A2000) |
| RAM            | ≥ 32 GB                               |
| OS             | Linux (systemd), macOS, or Windows 11 |

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
