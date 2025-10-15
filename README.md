# Ollama Dev‑First — Local‑Only (v3)

This package contains a single script to configure **Ollama for software development** on a local machine, including **root‑level systemd env overrides** and **on‑demand persona creation**.

## Quick Start

### Root/systemd mode (recommended if Ollama runs as a system service)
```bash
sudo python3 setup_ollama_local.py --global-env --threads 12
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

### Without sudo (user fallback)
```bash
python3 setup_ollama_local.py --global-env --threads 12
# Then re-source your shell and/or restart user services:
systemctl --user daemon-reload && systemctl --user restart ollama
```

### Personas (create on demand)
Available: `dev, arch, test, plan, planlite, orch`
```bash
# Pull bases + create dev + plan
python3 setup_ollama_local.py --pull --create --persona dev,plan

# Create after already pulling
python3 setup_ollama_local.py --create --persona arch,test

# List
python3 setup_ollama_local.py --list
```

### Run
```bash
ollama run dev-agent
ollama run arch-agent
ollama run test-agent
ollama run plan-agent
ollama run plan-lite-agent
ollama run orch-agent    # CPU-only
```

## Default envs applied
```
OLLAMA_NUM_GPU=1
OLLAMA_GPU_LAYERS=999
OLLAMA_NUM_THREADS=12
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_KEEP_ALIVE=10m
CUDA_VISIBLE_DEVICES=0
OLLAMA_FLASH_ATTENTION=1
```

## Why these models?
- **Qwen2.5 Coder 14B** for dev/test: excellent coding capability with good VRAM fit (16 GB) when quantized (q5).
- **DeepSeek-R1 Distill (Qwen 14B)** for architecture: stronger step‑by‑step reasoning for system design.
- **Qwen2.5 14B/7B** for planning: balanced quality vs. speed for spec‑driven workflows.
- **Llama3.1 8B** as a CPU‑only orchestrator: saves VRAM and coordinates tasks locally.

## Notes
- Keep one hot model (`OLLAMA_MAX_LOADED_MODELS=1`) to avoid VRAM thrash with IDE/Docker running.
- Use `num_ctx` 4k–8k locally. Very large contexts should be offloaded to some cloud workflow if ever needed.
