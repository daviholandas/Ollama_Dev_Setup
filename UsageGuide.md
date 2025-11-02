# 📖 VLLM Local Setup - Usage Guide

Complete guide for using the VLLM local setup with examples, API reference, and integration patterns.

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [API Reference](#api-reference)
4. [Tool Calling](#tool-calling)
5. [Agent-Specific Guides](#agent-specific-guides)
6. [IDE Integration](#ide-integration)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Full Installation

```bash
cd LLM_Local_Setup
python3 setup.py install
```

This command:
1. Checks prerequisites (GPU, Docker, NVIDIA toolkit)
2. Creates directory structure (`tools/`, `logs/`, `outputs/`, `workspace/`)
3. Generates tool definitions JSON files
4. Creates `docker-compose.yml`
5. Pulls VLLM Docker image (~8GB download)

**Time:** 5-10 minutes (depending on internet speed)

### Verify Installation

```bash
# List available agents
python3 setup.py list

# Check Docker Compose
docker compose config

# Verify tool definitions
ls -lh tools/
```

---

## Basic Usage

### Starting Agents

```bash
# Start developer agent (most used)
python3 setup.py start dev

# Start architect agent
python3 setup.py start architect

# Start product owner agent
python3 setup.py start po
```

**Note:** Only ONE agent can run at a time on 16GB GPU.

### Checking Status

```bash
# Using setup script
python3 setup.py status

# Using Docker Compose
docker compose ps

# Check logs
docker compose logs -f dev-agent
```

### Stopping Agents

```bash
# Stop all agents
python3 setup.py stop

# Or using Docker Compose
docker compose down
```

### Switching Agents

```bash
# Stop current agent
python3 setup.py stop

# Start different agent
python3 setup.py start architect
```

---

## API Reference

All agents expose an OpenAI-compatible API.

### Base URLs

- **Architect:** `http://localhost:8000`
- **Developer:** `http://localhost:8001`
- **Product Owner:** `http://localhost:8002`

### Endpoints

#### 1. List Models

```bash
GET /v1/models
```

**Example:**

```bash
curl http://localhost:8001/v1/models
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dev",
      "object": "model",
      "created": 1234567890,
      "owned_by": "vllm"
    }
  ]
}
```

#### 2. Chat Completions

```bash
POST /v1/chat/completions
```

**Example:**

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [
      {"role": "system", "content": "You are a helpful coding assistant."},
      {"role": "user", "content": "Write a Python function to reverse a string"}
    ],
    "temperature": 0.3,
    "max_tokens": 500
  }'
```

**Response:**

```json
{
  "id": "cmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "dev",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here's a Python function to reverse a string:\n\n```python\ndef reverse_string(s: str) -> str:\n    return s[::-1]\n```"
      },
      "finish_reason": "stop"
    }
  ]
}
```

#### 3. Streaming Completions

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [{"role": "user", "content": "Explain asyncio"}],
    "stream": true
  }'
```

---

## Tool Calling

### Available Tools

#### All Agents

**read_file**
```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read contents of a file",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "Path to the file"}
      },
      "required": ["path"]
    }
  }
}
```

**write_file**
```json
{
  "type": "function",
  "function": {
    "name": "write_file",
    "description": "Write content to a file",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "File path"},
        "content": {"type": "string", "description": "Content to write"}
      },
      "required": ["path", "content"]
    }
  }
}
```

**list_directory**
```json
{
  "type": "function",
  "function": {
    "name": "list_directory",
    "description": "List contents of a directory",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "Directory path"}
      },
      "required": ["path"]
    }
  }
}
```

#### Developer Agent Only

**execute_code**
```json
{
  "type": "function",
  "function": {
    "name": "execute_code",
    "description": "Execute Python code in sandbox",
    "parameters": {
      "type": "object",
      "properties": {
        "code": {"type": "string", "description": "Python code to execute"},
        "timeout": {"type": "integer", "default": 30, "description": "Timeout in seconds"}
      },
      "required": ["code"]
    }
  }
}
```

### Tool Calling Example (Python)

```python
import requests

# Load tool definitions
import json
with open('tools/dev-tools.json') as f:
    tools = json.load(f)

# Make request with tools
response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "dev",
        "messages": [
            {
                "role": "user",
                "content": "Read the file setup.py and tell me what the main() function does"
            }
        ],
        "tools": tools,
        "tool_choice": "auto"  # Let model decide when to use tools
    }
)

result = response.json()
print(result['choices'][0]['message']['content'])
```

### Tool Calling Example (cURL)

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "model": "dev",
  "messages": [
    {
      "role": "user",
      "content": "Create a new Python file called hello.py with a function that prints Hello World"
    }
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
}
EOF
```

---

## Agent-Specific Guides

### Architect Agent

**Best for:** System design, architecture decisions, high-level planning

**Port:** 8000  
**Model:** Qwen2.5-14B-Instruct-AWQ (11GB VRAM)  
**Temperature:** 0.1 (deterministic)

**Example Use Cases:**

```bash
# Microservices design
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "architect",
    "messages": [{
      "role": "user",
      "content": "Design a scalable microservices architecture for a real-time chat application with 1M+ users. Include message queue, database choices, and caching strategy."
    }],
    "temperature": 0.1,
    "max_tokens": 2000
  }'

# Technology selection
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "architect",
    "messages": [{
      "role": "user",
      "content": "Compare PostgreSQL vs MongoDB for an e-commerce product catalog. Consider: query patterns, scalability, transactions, schema flexibility."
    }]
  }'
```

### Developer Agent

**Best for:** Code generation, debugging, implementation, refactoring

**Port:** 8001  
**Model:** Qwen2.5-Coder-14B-Instruct-GPTQ (13GB VRAM)  
**Temperature:** 0.3 (balanced)

**Example Use Cases:**

```python
import requests

# Code generation with file writing
response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "dev",
        "messages": [{
            "role": "user",
            "content": "Create a FastAPI application with user authentication endpoints (register, login, logout) using JWT tokens"
        }],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "write_file",
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
        ],
        "temperature": 0.3
    }
)

# Debugging with code execution
response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "dev",
        "messages": [{
            "role": "user",
            "content": "Debug this code and tell me why it's not working: [paste code]"
        }],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "execute_code",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "timeout": {"type": "integer"}
                        },
                        "required": ["code"]
                    }
                }
            }
        ]
    }
)
```

### Product Owner Agent

**Best for:** User stories, requirements, sprint planning

**Port:** 8002  
**Model:** Qwen2.5-7B-Instruct-AWQ (5GB VRAM)  
**Temperature:** 0.5 (creative)

**Example Use Cases:**

```bash
# User story generation
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "po",
    "messages": [{
      "role": "user",
      "content": "Create 5 user stories for a mobile payment feature with biometric authentication. Include acceptance criteria for each."
    }],
    "temperature": 0.5,
    "max_tokens": 1500
  }'

# Requirements analysis
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "po",
    "messages": [{
      "role": "user",
      "content": "Analyze the requirements for a food delivery app MVP. Prioritize features for the first sprint."
    }]
  }'
```

---

## IDE Integration

### VS Code Integration

Create a custom task in `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Ask AI Developer",
      "type": "shell",
      "command": "curl",
      "args": [
        "http://localhost:8001/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-d", "{\"model\":\"dev\",\"messages\":[{\"role\":\"user\",\"content\":\"${input:prompt}\"}]}"
      ]
    }
  ],
  "inputs": [
    {
      "id": "prompt",
      "type": "promptString",
      "description": "Ask the AI developer"
    }
  ]
}
```

### Continue.dev Integration

Add to Continue config:

```json
{
  "models": [
    {
      "title": "Local Developer",
      "provider": "openai",
      "model": "dev",
      "apiBase": "http://localhost:8001/v1",
      "apiKey": "sk-dummy"
    }
  ]
}
```

### Cursor Integration

In Cursor settings, add custom model:

```
Base URL: http://localhost:8001/v1
Model: dev
API Key: (any value)
```

---

## Advanced Configuration

### Modify Model Parameters

Edit `docker-compose.yml`:

```yaml
command: >
  --model Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ
  --served-model-name dev
  --gpu-memory-utilization 0.90
  --max-model-len 16384        # Increase context length
  --enable-prefix-caching
  --tensor-parallel-size 1      # Use multiple GPUs
  --temperature 0.3             # Default temperature
```

### Use Different Models

Replace model in `docker-compose.yml`:

```yaml
# Use smaller model (uses less VRAM)
command: >
  --model Qwen/Qwen2.5-7B-Instruct-AWQ
  ...

# Use larger model (requires more VRAM)
command: >
  --model Qwen/Qwen2.5-32B-Instruct-AWQ
  ...
```

### Add Custom Tools

Edit `tools/dev-tools.json`:

```json
[
  {
    "type": "function",
    "function": {
      "name": "run_tests",
      "description": "Run test suite",
      "parameters": {
        "type": "object",
        "properties": {
          "test_path": {"type": "string"},
          "framework": {"type": "string", "enum": ["pytest", "unittest"]}
        },
        "required": ["test_path"]
      }
    }
  }
]
```

---

## Troubleshooting

### Issue: Agent Won't Start

**Symptoms:** Container starts then immediately stops

**Solutions:**

```bash
# Check logs
docker compose logs dev-agent

# Common causes:
# 1. GPU out of memory - stop other agents first
python3 setup.py stop

# 2. NVIDIA toolkit issue - restart Docker
sudo systemctl restart docker

# 3. Model download issue - check internet and disk space
df -h
```

### Issue: Slow Response Time

**Symptoms:** First request takes 60+ seconds

**This is normal!** Model needs to load into GPU memory.

**Solutions:**

```bash
# Keep agent running (don't restart frequently)
# Pre-warm with a simple request
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"dev","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

### Issue: Out of Memory

**Symptoms:** Container crashes, OOM errors in logs

**Solutions:**

```bash
# Use smaller agent
python3 setup.py stop
python3 setup.py start po  # Uses only 5GB

# Reduce GPU memory utilization
# Edit docker-compose.yml:
# VLLM_GPU_MEMORY_UTILIZATION=0.80  # From 0.90

# Reduce context length
# Edit command in docker-compose.yml:
# --max-model-len 8192  # From 16384
```

### Issue: Tool Calls Not Working

**Symptoms:** Agent doesn't use tools or errors on tool calls

**Solutions:**

```bash
# Verify tool definitions exist
ls -lh tools/

# Check VLLM tool calling is enabled
docker compose logs dev-agent | grep "tool"

# Ensure using correct parser
# In docker-compose.yml:
# VLLM_TOOL_CALL_PARSER=hermes

# Test tool definition format
python3 -m json.tool tools/dev-tools.json
```

---

## Performance Tips

1. **First request is slow** - Model loading takes 60-90s
2. **Keep agent running** - Restarting loses GPU cache
3. **Use prefix caching** - Enabled by default, repeated prompts are faster
4. **Batch requests** - VLLM automatically batches concurrent requests
5. **Monitor GPU** - `watch -n1 nvidia-smi`
6. **Context length** - Shorter contexts = faster inference
7. **Temperature** - Lower values (0.1-0.3) are faster than high (0.7-0.9)

---

## Additional Resources

- **VLLM Documentation:** https://docs.vllm.ai/
- **OpenAI API Reference:** https://platform.openai.com/docs/api-reference
- **Tool Calling Guide:** https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#tool-calling
- **Model Hub:** https://huggingface.co/Qwen

---

**Last Updated:** 2025-11  
**Version:** 2.0
