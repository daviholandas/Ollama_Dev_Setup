# 🚀 Quick Start Guide

## ⚡ Installation (One-Time Setup)

### 1. Configure Global Environment

```bash
# With sudo (recommended for systemd service)
sudo python3 setup_ollama_local.py --global-env --threads 8
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Verify service is running
sudo systemctl status ollama
```

### 2. Pull Base Models & Create Personas

```bash
# Essential personas (recommended to start)
python3 setup_ollama_local.py --pull --create --persona dev,arch,test,orch

# Full suite (all personas)
python3 setup_ollama_local.py --pull --create --persona dev,arch,test,plan,planlite,orch,review,debug,refactor,docs
```

> ⏱️ **Estimated Time**: 30-60 minutes depending on internet speed

---

## 🎯 Usage Examples

### Development

```bash
# Start development agent
ollama run dev-agent

# Example prompt
"Create a REST API controller for user management with CRUD operations, 
validation, error handling, and proper HTTP status codes"
```

### Architecture

```bash
ollama run arch-agent

# Example prompt
"Design a microservices architecture for an e-commerce platform. 
Consider API gateway, service discovery, event-driven communication, 
and database per service pattern"
```

### Testing

```bash
ollama run test-agent

# Example prompt
"Generate comprehensive xUnit tests for this UserService class: [paste code]
Include unit tests, integration tests, edge cases, and mocking examples"
```

### Code Review

```bash
ollama run review-agent

# Example prompt
"Review this code for security vulnerabilities, performance issues, 
and maintainability problems: [paste code]"
```

### Debugging

```bash
ollama run debug-agent

# Example prompt
"Analyze this error and provide root cause analysis: 
System.InvalidOperationException: A second operation was started on this context 
before a previous operation completed..."
```

### Planning

```bash
ollama run plan-agent

# Example prompt
"Create a detailed spec for implementing OAuth2 authentication 
with JWT tokens, refresh tokens, and role-based authorization"
```

---

## 📊 Model Overview

| Persona | Model Size | VRAM Usage | Best For |
|---------|-----------|------------|----------|
| **orch** | 3B (q5) | ~2.5 GB | Quick routing decisions |
| **planlite** | 7B (q5) | ~5 GB | Fast agile planning |
| **docs** | 7B (q5) | ~5 GB | Documentation writing |
| **test** | 14B (q5) | ~10 GB | Test generation |
| **plan** | 14B (q5) | ~9 GB | Detailed project planning |
| **review** | 14B (q5) | ~10 GB | Code review & analysis |
| **refactor** | 14B (q5) | ~10 GB | Code refactoring |
| **dev** | 32B (q4) | ~10 GB GPU + 8 GB RAM | Complex coding tasks |
| **arch** | 32B (q4) | ~10 GB GPU + 8 GB RAM | Architecture decisions |
| **debug** | 32B (q4) | ~10 GB GPU + 8 GB RAM | Deep debugging |

> 💡 **Tip**: Start with smaller models (3B-14B) for faster responses, use 32B for complex tasks

---

## 🔧 Common Commands

### List Available Personas

```bash
python3 setup_ollama_local.py --list
```

### Check Running Models

```bash
ollama ps
```

### Stop a Model (Free VRAM)

```bash
ollama stop dev-agent
```

### Monitor GPU Usage

```bash
# Real-time GPU monitoring
nvidia-smi -l 1

# or use
watch -n 1 nvidia-smi
```

### Test Model Response

```bash
ollama run dev-agent "Explain SOLID principles briefly"
```

---

## 🐛 Troubleshooting

### Ollama Service Not Starting

```bash
# Check logs
sudo journalctl -u ollama -f

# Restart service
sudo systemctl restart ollama
```

### Out of VRAM

```bash
# Stop current model
ollama stop <model-name>

# Use smaller model or reduce context
# Edit params in setup_ollama_local.py
```

### Slow Response Times

```bash
# Check if model is fully loaded in GPU
nvidia-smi

# Verify Flash Attention is enabled
echo $OLLAMA_FLASH_ATTENTION  # Should output: 1

# Increase threads if not using IDEs heavily
sudo python3 setup_ollama_local.py --global-env --threads 12
```

### Model Not Found

```bash
# Pull the base model first
ollama pull qwen2.5-coder:32b-instruct-q4_K_M

# Then recreate persona
python3 setup_ollama_local.py --create --persona dev
```

---

## 📚 Recommended Workflow

1. **Start with orchestrator** → `ollama run orch-agent`
2. **Get routing suggestion** → Based on your task
3. **Switch to specific persona** → `ollama run <recommended-agent>`
4. **Work on task** → Provide detailed context
5. **Review with review-agent** → Quality check
6. **Test with test-agent** → Generate tests
7. **Document with docs-agent** → Create documentation

---

## ⚙️ Advanced Configuration

### Adjust Thread Count (Default: 8)

```bash
sudo python3 setup_ollama_local.py --global-env --threads 12
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

### Custom Persona Parameters

Edit `setup_ollama_local.py` and modify the `PERSONAS` dictionary:

```python
"dev": {
  "params": {
    "num_ctx": "32768",  # Context window size
    "temperature": "0.2",  # Creativity (0.0-1.0)
    "num_predict": "2048"  # Max output tokens
  }
}
```

### Environment Variables

Located in `DEFAULT_ENVS` dictionary:

```python
"OLLAMA_NUM_THREADS": "8",      # CPU threads for inference
"OLLAMA_KEEP_ALIVE": "5m",       # Model cache duration
"OLLAMA_MAX_LOADED_MODELS": "1", # Simultaneous models
"OLLAMA_FLASH_ATTENTION": "1"    # Enable Flash Attention (RTX 30xx+)
```

---

## 🎓 Tips & Best Practices

1. **Use appropriate persona for the task** - Don't use 32B models for simple questions
2. **Provide context** - More context = better responses
3. **Iterate gradually** - Start broad, then narrow down
4. **Monitor VRAM** - Especially when running IDEs + Docker
5. **Keep models cached** - Frequent context switches = slower
6. **Use stop sequences** - Prevent code block overflow with `stop: "```"`
7. **Batch similar tasks** - Stay in one persona for related work

---

## 📖 Further Reading

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [Modelfile Reference](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)
- [Qwen2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct)
- [GGUF Quantization Guide](https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md)

---

**Need help?** Check the main [README.md](README.md) for detailed information.
