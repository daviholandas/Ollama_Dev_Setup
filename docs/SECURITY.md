# 🔐 VLLM Security Guide

## API Key Authentication

All VLLM agents now require API key authentication for secure access.

---

## Setup API Key

### 1. Generate a Secure API Key

```bash
# Generate a random secure key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output:
```
8K9mP2nQ5rS7tU1vW3xY6zA4bC8dE2fG9hJ5kL8mN2pQ5rS7tU1vW
```

### 2. Create `.env` File

```bash
# Copy example file
cp .env.example .env

# Edit with your API key
nano .env
```

Set your API key in `.env`:
```bash
VLLM_API_KEY=your-generated-secure-key-here
```

### 3. Start Agents with API Key

```bash
# Load environment variables and start
source .env
python3 setup.py start dev

# OR using docker compose directly
docker compose up -d dev-agent
```

---

## Using API with Authentication

### cURL Examples

**Without API key (will fail):**
```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "dev", "messages": [{"role": "user", "content": "Hello"}]}'
# Returns: 401 Unauthorized
```

**With API key (works):**
```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{"model": "dev", "messages": [{"role": "user", "content": "Hello"}]}'
```

### Python Examples

```python
import requests

API_KEY = "your-api-key-here"  # Load from .env in production
BASE_URL = "http://localhost:8001/v1"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json={
        "model": "dev",
        "messages": [
            {"role": "user", "content": "Write a Python function"}
        ]
    }
)

print(response.json())
```

### Using Environment Variables (Recommended)

```python
import os
import requests
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

API_KEY = os.getenv("VLLM_API_KEY")
BASE_URL = "http://localhost:8001/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json={
        "model": "dev",
        "messages": [{"role": "user", "content": "Hello"}]
    }
)
```

### OpenAI Python Client

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key=os.getenv("VLLM_API_KEY")
)

response = client.chat.completions.create(
    model="dev",
    messages=[
        {"role": "user", "content": "Write a hello world function"}
    ]
)

print(response.choices[0].message.content)
```

---

## Context Length Limitations

### Memory vs Context Length

Your 16GB GPU has limitations on maximum context length:

| Model | Max Safe Context | Memory Used |
|-------|------------------|-------------|
| **7B-AWQ** | 32k-48k | ~12-15GB |
| **14B-AWQ** | 16k-24k | ~11-18GB |
| **14B-GPTQ** | 16k-24k | ~13-20GB |

### Testing Maximum Context

```bash
# Test with smaller context first
curl http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer $VLLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

### Increase Context for 7B Model

If you need >47k context, use the 7B model:

**Edit `docker-compose.yml`:**
```yaml
dev-agent:
  command: --model Qwen/Qwen2.5-7B-Instruct-AWQ
    --served-model-name dev
    --gpu-memory-utilization 0.85
    --max-model-len 49152  # 48k context
    --enable-prefix-caching
    --enable-auto-tool-choice
    --tool-call-parser hermes
    --api-key ${VLLM_API_KEY}
    --port 8000
```

**Restart:**
```bash
docker compose restart dev-agent
```

### Monitor GPU Memory

```bash
# Watch GPU memory usage
watch -n1 nvidia-smi

# Check specific agent memory
docker stats vllm-dev-agent
```

---

## Security Best Practices

### 1. Never Commit API Keys

Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### 2. Rotate Keys Regularly

```bash
# Generate new key
NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env
echo "VLLM_API_KEY=$NEW_KEY" > .env

# Restart agents
docker compose restart
```

### 3. Network Security

**Localhost only (default):**
```yaml
ports:
  - "127.0.0.1:8001:8000"  # Only accessible from localhost
```

**Expose to network (use with caution):**
```yaml
ports:
  - "0.0.0.0:8001:8000"  # Accessible from any IP
```

### 4. Use HTTPS in Production

For production deployments, use a reverse proxy with TLS:

```nginx
# nginx config
server {
    listen 443 ssl;
    server_name vllm.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }
}
```

---

## Troubleshooting

### API Key Not Working

```bash
# Check if environment variable is set
echo $VLLM_API_KEY

# Reload environment
source .env

# Verify agent has the key
docker compose exec dev-agent env | grep VLLM_API_KEY

# Check logs
docker compose logs dev-agent | grep -i auth
```

### 401 Unauthorized Error

```bash
# Ensure you're passing the Authorization header
curl -H "Authorization: Bearer YOUR_KEY" http://localhost:8001/v1/models

# Check if key matches
docker compose exec dev-agent printenv VLLM_API_KEY
```

### Out of Memory with Large Context

```bash
# Reduce max context length
# Edit docker-compose.yml:
--max-model-len 16384  # Instead of 49152

# OR use smaller model
--model Qwen/Qwen2.5-7B-Instruct-AWQ  # Instead of 14B

# OR reduce GPU memory utilization
--gpu-memory-utilization 0.80  # Instead of 0.90
```

---

## Additional Resources

- **VLLM Security Docs:** https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#authentication
- **OpenAI API Reference:** https://platform.openai.com/docs/api-reference/authentication
- **Environment Variables:** https://docs.docker.com/compose/environment-variables/

---

**Last Updated:** 2025-11  
**Version:** 2.0
