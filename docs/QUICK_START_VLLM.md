# ⚡ Quick Start Guide - VLLM Multi-Agent Setup

Get up and running with VLLM-powered AI agents in **3 steps** (30-45 minutes).

---

## Prerequisites

**Hardware**:
- GPU: NVIDIA RTX 4060+ (8GB min) or RTX 5060 Ti (recommended)
- CPU: 8-core minimum (16-core optimal)
- RAM: 32GB+ (64GB recommended)
- Disk: 100GB free (for models + Docker)

**Software**:
- Ubuntu 22.04 LTS or similar Linux
- Docker 20.10+
- NVIDIA Container Toolkit

---

## Step 1: Install Dependencies (10-15 minutes)

### 1a. Download the setup script

```bash
cd ~/Projects/Ollama_Dev_Setup
chmod +x setup_vllm.py
```

### 1b. Run automated setup

```bash
python3 setup_vllm.py --install-dependencies --setup-docker
```

**What this does**:
- ✅ Validates NVIDIA drivers and CUDA
- ✅ Installs Docker and NVIDIA Container Toolkit
- ✅ Downloads VLLM and quantization libraries
- ✅ Creates `/models` directory structure

**Expected output**:
```
[✓] CUDA 12.2 detected (compute capability 8.9)
[✓] Docker daemon running
[✓] NVIDIA Container Toolkit installed
[✓] VLLM 0.3.0+ installed
[✓] Setup complete!
```

---

## Step 2: Download Models (10-20 minutes)

Models download automatically, or run manually:

```bash
python3 setup_vllm.py --download-models
```

**Models downloaded**:
- Qwen2.5:32B-Instruct (Architect) — 19 GB
- Qwen2.5-Coder:32B-Instruct (Dev) — 19 GB
- Qwen2.5:7B-Instruct (P.O.) — 4.2 GB

**Total**: ~42 GB (compressed to 13-15 GB with quantization)

**Expected output**:
```
Downloading Qwen/Qwen2.5-32B-Instruct...
Downloaded to ./models/Qwen2.5-32B-Instruct
✓ All models ready
```

---

## Step 3: Launch Your First Agent (2-5 minutes)

### 3a. Start the P.O. Agent (fastest)

```bash
python3 agent_manager.py --launch po
```

**What happens**:
1. Docker container starts
2. Model loads to GPU (40 seconds)
3. Server ready on `http://localhost:8002`

**Expected output**:
```
🚀 Launching P.O. Agent...
⏳ Waiting for container health check...
🟢 P.O. Agent running on http://localhost:8002
```

### 3b. Test the agent

In another terminal:

```bash
curl http://localhost:8002/v1/models
```

**Expected response**:
```json
{
  "object": "list",
  "data": [
    {"id": "Qwen2.5-7B-Instruct", "object": "model", "owned_by": "ollama"}
  ]
}
```

### 3c. Send your first prompt

```bash
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2.5-7B-Instruct",
    "messages": [{"role": "user", "content": "What is a user story?"}],
    "max_tokens": 200
  }' | jq '.choices[0].message.content'
```

**Expected output**:
```
"A user story is a simple, clear description of a feature or functionality from the
user's perspective. It typically follows the format: 'As a [user type], I want
[capability] so that [benefit]'. User stories help teams understand user needs..."
```

---

## Next Steps: Using the Agents

### Switch Agents

Stop P.O., start Developer:

```bash
python3 agent_manager.py --switch dev
```

Expected time: 2-5 seconds

### Send a coding request

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2.5-Coder-32B-Instruct",
    "messages": [{
      "role": "user",
      "content": "Write a Python function to validate email addresses"
    }],
    "max_tokens": 500
  }' | jq '.choices[0].message.content'
```

### Use Python client

```python
from openai import OpenAI

# P.O. Agent
po_client = OpenAI(api_key="sk-not-needed", base_url="http://localhost:8002/v1")
response = po_client.chat.completions.create(
    model="Qwen2.5-7B-Instruct",
    messages=[{"role": "user", "content": "Create a user story for a login feature"}],
    temperature=0.5
)
print(response.choices[0].message.content)

# Dev Agent
dev_client = OpenAI(api_key="sk-not-needed", base_url="http://localhost:8001/v1")
code_response = dev_client.chat.completions.create(
    model="Qwen2.5-Coder-32B-Instruct",
    messages=[{"role": "user", "content": "Implement the login endpoint"}],
    temperature=0.3
)
print(code_response.choices[0].message.content)
```

---

## Agent Manager CLI Reference

### Launch agent

```bash
python3 agent_manager.py --launch {architect|dev|po}
```

### Stop agent

```bash
python3 agent_manager.py --stop architect
```

### Switch agent

```bash
python3 agent_manager.py --switch dev
```

### View status

```bash
python3 agent_manager.py --status
```

**Output**:
```
🟢 Architect: Running (Qwen2.5:32B)
🔴 Developer: Stopped
🟢 P.O.: Running (Qwen2.5:7B)
```

### View logs

```bash
python3 agent_manager.py --logs po
```

### GPU monitoring

```bash
python3 agent_manager.py --gpu-stats
```

**Output**:
```
GPU 0: VRAM 7.2GB / 16.0GB (45%)
Temperature: 65°C
Power: 180W
```

### List agents

```bash
python3 agent_manager.py --list
```

**Output**:
```
Available Agents:
  architect: Qwen2.5:32B-Instruct (32K context)
  dev:       Qwen2.5-Coder:32B-Instruct (32K context)
  po:        Qwen2.5:7B-Instruct (7K context)
```

### Test API

```bash
python3 agent_manager.py --test-api po
```

---

## Workflow Example: End-to-End Development

### Phase 1: Planning (P.O. Agent)

```bash
python3 agent_manager.py --launch po
```

**Prompt**:
> "Create 3 user stories for a payment system. Each should follow: 'As a [role], I want [feature] so that [benefit]'"

### Phase 2: Architecture (Architect Agent)

```bash
python3 agent_manager.py --switch architect
```

**Prompt**:
> "Design a microservices architecture for the payment system described earlier. Include database schema, API contracts, and error handling strategy."

### Phase 3: Implementation (Developer Agent)

```bash
python3 agent_manager.py --switch dev
```

**Prompt**:
> "Implement the payment service based on the architecture. Use FastAPI, include error handling, and add unit tests."

### Phase 4: Review (Back to Developer or Architect)

```bash
python3 agent_manager.py --switch architect
```

**Prompt**:
> "Review the implementation and suggest improvements for scalability, security, and maintainability."

---

## Troubleshooting

### Issue: "CUDA out of memory"

**Solution**:
```bash
# Try smaller model first
python3 agent_manager.py --launch po

# Reduce GPU utilization in docker-compose-architect.yml
VLLM_GPU_MEMORY_UTILIZATION: 0.75  # Changed from 0.85
```

### Issue: "Container failed to start"

**Solution**:
```bash
# Check logs
python3 agent_manager.py --logs architect

# Restart Docker
sudo systemctl restart docker

# Rebuild container
docker-compose -f docker-compose-architect.yml down
docker-compose -f docker-compose-architect.yml up -d
```

### Issue: "Slow inference (< 20 tokens/sec)"

**Solution**:
```bash
# Check GPU utilization
python3 agent_manager.py --gpu-stats

# If < 80% utilized, restart agent
python3 agent_manager.py --stop architect
python3 agent_manager.py --launch architect
```

### Issue: Model download timeout

**Solution**:
```bash
# Retry with longer timeout
HF_HUB_DOWNLOAD_TIMEOUT=3600 python3 setup_vllm.py --download-models

# Or manual download
huggingface-cli download Qwen/Qwen2.5-32B-Instruct \
  --cache-dir ./models \
  --local-dir-use-symlinks False
```

---

## Performance Tips

### Enable Prefix Caching

Already enabled by default (VLLM_ENABLE_PREFIX_CACHING=1)

**Benefit**: 10-30% faster for repeated prompts

### Keep Models Loaded

Don't switch agents frequently during development. Each switch:
- Unloads current model (2s)
- Loads new model (40s)
- Total: ~42 seconds

### Use Smaller Context for P.O.

P.O. agent (7B model) completes 40% faster than 32B models.
Perfect for quick requirements gathering.

### Batch Requests

Make multiple requests without switching agents:
```python
from openai import OpenAI

client = OpenAI(api_key="sk-not-needed", base_url="http://localhost:8001/v1")

prompts = [
    "Implement user signup",
    "Implement user login",
    "Implement password reset"
]

for prompt in prompts:
    response = client.chat.completions.create(
        model="Qwen2.5-Coder-32B-Instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response.choices[0].message.content)
```

---

## Integration with Development Tools

### VS Code Extension

Create `.vscode/settings.json`:
```json
{
  "github.copilot.advanced": {
    "chatgpt.url": "http://localhost:8001/v1",
    "chatgpt.model": "Qwen2.5-Coder-32B-Instruct"
  }
}
```

### IDE Integration

Most IDEs support OpenAI-compatible APIs:
- **VS Code**: GitHub Copilot Chat
- **JetBrains**: Built-in AI assistant
- **Neovim**: codeium.nvim

---

## Next: Advanced Topics

Ready to dive deeper?

1. **[VLLM Comprehensive Guide](./VLLM_COMPREHENSIVE_GUIDE.md)** — Full architecture, tuning, and optimization
2. **[Performance Tuning](./PARAMETER_OPTIMIZATION_SUMMARY.md)** — GPU memory, batch size, context length
3. **[Model Comparison](./MODEL_CHOICES.md)** — Why Qwen over Llama/Mistral
4. **[System Prompts](./SYSTEM_PROMPTS.md)** — Custom instructions per agent

---

## Support

**GitHub Issues**: [Report bugs](https://github.com/your-repo/issues)  
**Documentation**: See `/docs` folder  
**Community**: Discord/Slack (if available)

---

**Last Updated**: October 2025  
**Version**: 1.0  
**Status**: Ready to Use ✅
