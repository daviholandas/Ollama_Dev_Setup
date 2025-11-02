# 🚀 VLLM Local Setup

**High-Performance Local LLM Inference with Tool Integration**

Run powerful AI agents locally using VLLM — 2-4× faster than Ollama, with native tool calling support for IDE and CLI integration.

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-blue.svg)]()
[![VLLM](https://img.shields.io/badge/vLLM-latest-orange.svg)](https://github.com/vllm-project/vllm)
[![Docker](https://img.shields.io/badge/Docker-required-blue.svg)](https://docs.docker.com/get-docker/)

---

## 📋 Overview

Complete setup for running Large Language Models locally using VLLM with:

- **🚀 High Performance** - PagedAttention, continuous batching, 2-4× faster inference
- **🔧 Tool Calling** - Native support for file operations, code execution, IDE integration
- **🤖 Three Specialized Agents** - Purpose-built for different development tasks
- **🐳 Docker Containerized** - Simple one-command deployment
- **🔐 Fully Local** - All inference on your machine, zero cloud dependencies

### Why VLLM?

| Feature | Ollama | VLLM | Benefit |
|---------|--------|------|---------|
| **Throughput** | ~20 tok/s | 50-80 tok/s | 2-4× faster |
| **Memory** | High | Optimized (PagedAttention) | Fit larger models |
| **Batching** | Static | Continuous | Better GPU utilization |
| **Tool Calling** | Limited | Native | Full IDE/CLI integration |

---

## 🤖 The Three Agents

| Agent | Model | Port | GPU Memory | Use Case |
|-------|-------|------|------------|----------|
| **Architect** | Qwen2.5-14B-AWQ | 8000 | ~11GB | System design, architecture planning |
| **Developer** | Qwen2.5-Coder-14B-GPTQ | 8001 | ~13GB | Code generation, debugging, implementation |
| **Product Owner** | Qwen2.5-7B-AWQ | 8002 | ~5GB | Requirements, user stories, planning |

**Note:** Only one agent runs at a time on 16GB GPU setups.

---

## 📦 Prerequisites

Before installation, ensure you have:

- **NVIDIA GPU** with 8GB+ VRAM (16GB recommended)
- **Docker** (20.10+) with GPU support
- **NVIDIA Container Toolkit** installed
- **CUDA 12.x** drivers
- **Python 3.8+**

### Quick Prerequisite Check

```bash
# Check GPU
nvidia-smi

# Check Docker
docker --version

# Check NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

# Check Docker Compose
docker compose version
```

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install

```bash
cd LLM_Local_Setup
python3 setup.py install
```

This will:
- ✅ Validate prerequisites (GPU, Docker, NVIDIA Container Toolkit)
- ✅ Create directory structure
- ✅ Generate tool definitions (read_file, write_file, execute_code, etc.)
- ✅ Create docker-compose.yml
- ✅ Pull VLLM Docker image

### Step 2: Start an Agent

```bash
# Start Developer Agent (most commonly used)
python3 setup.py start dev

# OR Architect Agent
python3 setup.py start architect

# OR Product Owner Agent
python3 setup.py start po
```

**Wait 60-90 seconds** for the model to load into GPU memory.

### Step 3: Use the Agent

Once running, the agent exposes an OpenAI-compatible API:

```bash
# Test the connection
curl http://localhost:8001/v1/models

# Chat completion
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [
      {"role": "user", "content": "Write a Python function to calculate fibonacci"}
    ],
    "max_tokens": 500
  }'
```

---

## 🛠️ Management Commands

```bash
# Check status
python3 setup.py status

# Stop all agents
python3 setup.py stop

# List available agents
python3 setup.py list

# Switch agents
python3 setup.py stop
python3 setup.py start architect
```

**OR use Docker Compose directly:**

```bash
docker compose ps                    # Check status
docker compose logs -f dev-agent     # View logs
docker compose restart dev-agent     # Restart
docker compose down                  # Stop all
```

---

## 🔧 Tool Integration

Each agent supports tool calling for IDE and CLI integration.

### Available Tools

**All Agents:**
- `read_file` - Read file contents
- `write_file` - Write to files
- `list_directory` - List directory contents

**Developer Agent (additional):**
- `execute_code` - Run Python code in sandbox

### Tool Definitions

Tool definitions are in `tools/*.json`:
- `tools/architect-tools.json` - Architect agent tools
- `tools/dev-tools.json` - Developer agent tools (includes code execution)
- `tools/po-tools.json` - Product Owner agent tools

### Example: Using Tools via Python

```python
import requests

response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "dev",
        "messages": [
            {"role": "user", "content": "Read the file setup.py and explain what it does"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file"
                            }
                        },
                        "required": ["path"]
                    }
                }
            }
        ]
    }
)

# The agent will call read_file tool and use the contents to answer
print(response.json())
```

### Example: Using Tools via cURL

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [
      {"role": "user", "content": "Create a new file hello.py with a hello world function"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "write_file",
          "description": "Write content to a file",
          "parameters": {
            "type": "object",
            "properties": {
              "path": {"type": "string"},
              "content": {"type": "string"}
            },
            "required": ["path", "content"]
          }
        }
      }
    ]
  }'
```

---

## 📁 Project Structure

```
LLM_Local_Setup/
├── setup.py                # Unified setup script (NEW)
├── docker-compose.yml      # All agents in one file (NEW)
├── tools/
│   ├── architect-tools.json
│   ├── dev-tools.json
│   └── po-tools.json
├── outputs/                # Agent outputs
├── logs/                   # Agent logs
│   ├── architect/
│   ├── dev/
│   └── po/
├── workspace/              # Code execution sandbox
├── README.md               # This file
└── UsageGuide.md           # Detailed usage guide
```

---

## 💡 Usage Examples

### Example 1: Architecture Design

```bash
# Start architect agent
python3 setup.py start architect

# Ask for system design
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "architect",
    "messages": [
      {"role": "user", "content": "Design a scalable microservices architecture for an e-commerce platform with user auth, product catalog, orders, and payments"}
    ]
  }'
```

### Example 2: Code Generation

```bash
# Start developer agent
python3 setup.py start dev

# Generate code with tool use
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [
      {"role": "user", "content": "Create a FastAPI app with user authentication endpoints"}
    ],
    "tools": [...]
  }'
```

### Example 3: Requirements Planning

```bash
# Start PO agent
python3 setup.py start po

# Generate user stories
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "po",
    "messages": [
      {"role": "user", "content": "Create user stories for a mobile payment feature with biometric authentication"}
    ]
  }'
```

---

## 🔍 Troubleshooting

### Agent Won't Start

```bash
# Check logs
docker compose logs dev-agent

# Check GPU memory
nvidia-smi

# Restart fresh
docker compose down
python3 setup.py start dev
```

### Out of GPU Memory

```bash
# Stop current agent first
python3 setup.py stop

# Use smaller model (PO agent uses only 5GB)
python3 setup.py start po
```

### Connection Refused

- Wait 60-90 seconds after starting (model loads into GPU)
- Check health: `docker compose ps`
- View logs: `docker compose logs -f dev-agent`

### NVIDIA Container Toolkit Not Found

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

---

## 🎯 Performance Tips

1. **Warm up time**: First request after starting takes 60-90s (model loading)
2. **GPU memory**: Only run ONE agent at a time on 16GB GPUs
3. **Context length**: Longer contexts use more memory, adjust `--max-model-len` if needed
4. **Batching**: VLLM automatically batches requests for better throughput
5. **Caching**: Prefix caching enabled - repeated prompts are faster

---

## 📚 Additional Resources

- **UsageGuide.md** - Detailed usage examples and API reference
- **VLLM Documentation** - https://docs.vllm.ai/
- **Tool Calling Guide** - https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#tool-calling

---

## 🔐 Security

- ✅ All inference runs locally (no cloud API calls)
- ✅ Models downloaded to `~/.cache/huggingface`
- ✅ Agents isolated in separate containers
- ⚠️ API exposed on localhost only (not exposed to network)
- ⚠️ Code execution sandbox enabled for dev-agent only

---

## 📜 License

MIT License - Free for personal and commercial use.

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new agent types
- Improve tool definitions
- Optimize model configurations
- Submit bug fixes

---

**Last Updated:** 2025-11  
**Version:** 2.0 (Unified Setup)  
**Status:** Production Ready ✅
