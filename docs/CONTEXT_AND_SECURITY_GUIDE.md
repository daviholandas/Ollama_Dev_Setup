# 🔑 Quick Reference: Context Length & API Security

## Summary of Your Questions

### ❓ Question 1: Can 16GB GPU handle >47k context?

**Answer: No for 14B models, Yes for 7B models**

| Model Size | Current Context | Max Context on 16GB | Memory at Max |
|------------|----------------|---------------------|---------------|
| **7B-AWQ** | 8k | ✅ **48k** | ~15GB |
| **14B-AWQ** | 16k | ⚠️ **24k-32k** | ~18GB |
| **14B-GPTQ** | 16k | ⚠️ **24k** | ~20GB |

**Memory formula:**
```
Total = Base_Model + (Context × Hidden_Dim × Layers × KV_Cache)
```

### ❓ Question 2: API Key Validation

**Answer: Implemented! ✅**

All agents now support API key authentication.

---

## 🚀 Quick Start with Security

### Step 1: Generate API Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Create `.env` File

```bash
# Copy example
cp .env.example .env

# Add your generated key
echo "VLLM_API_KEY=YOUR_GENERATED_KEY_HERE" > .env
```

### Step 3: Start Agent

```bash
# Load env and start
source .env
python3 setup.py start dev
```

### Step 4: Use with API Key

```bash
# Export for easy use
export VLLM_API_KEY="your-key-here"

# Test with authentication
curl http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer $VLLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"dev","messages":[{"role":"user","content":"Hello"}]}'
```

---

## 📊 Context Length Options

### Option A: Keep 14B, Modest Context (Recommended)

**Current setup - works perfectly:**
```yaml
# docker-compose.yml (no changes needed)
command: --model Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ
  --max-model-len 16384  # 16k context
  --gpu-memory-utilization 0.9
```

**Memory usage:** ~13GB  
**Context:** 16k tokens (~12k words)

### Option B: 14B with Maximum Safe Context

**Edit `docker-compose.yml`:**
```yaml
command: --model Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ
  --max-model-len 24576  # 24k context (50% more)
  --gpu-memory-utilization 0.95
```

**Memory usage:** ~15-16GB (tight!)  
**Context:** 24k tokens (~18k words)

### Option C: Switch to 7B for Large Context

**Edit `docker-compose.yml`:**
```yaml
command: --model Qwen/Qwen2.5-7B-Instruct-AWQ  # Changed from 14B
  --max-model-len 49152  # 48k context (3× more!)
  --gpu-memory-utilization 0.85
```

**Memory usage:** ~12-13GB  
**Context:** 48k tokens (~36k words)  
**Trade-off:** Smaller model, less capable but handles huge contexts

### Option D: 7B-Coder for Best Balance

**Edit `docker-compose.yml`:**
```yaml
command: --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ
  --max-model-len 32768  # 32k context (2× more)
  --gpu-memory-utilization 0.80
```

**Memory usage:** ~8-10GB  
**Context:** 32k tokens (~24k words)  
**Best for:** Coding with large codebases

---

## 🔐 API Authentication Examples

### Python with OpenAI Client

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key=os.getenv("VLLM_API_KEY")
)

response = client.chat.completions.create(
    model="dev",
    messages=[{"role": "user", "content": "Write a sorting function"}]
)

print(response.choices[0].message.content)
```

### Python with Requests

```python
import os
import requests

headers = {
    "Authorization": f"Bearer {os.getenv('VLLM_API_KEY')}",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    headers=headers,
    json={
        "model": "dev",
        "messages": [{"role": "user", "content": "Hello"}]
    }
)
```

### cURL

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer $VLLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dev",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const response = await fetch('http://localhost:8001/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.VLLM_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'dev',
    messages: [{role: 'user', content: 'Hello'}]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

---

## 🧪 Testing Context Limits

### Test Current Context

```bash
# Count tokens in your prompt (approximate: 1 token ≈ 0.75 words)
echo "Your prompt here" | wc -w  # Word count
# Multiply by 1.33 to get approximate tokens
```

### Test API with Long Context

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key=os.getenv("VLLM_API_KEY")
)

# Create a long prompt (test limits)
long_text = "Test context. " * 5000  # ~10k tokens

try:
    response = client.chat.completions.create(
        model="dev",
        messages=[
            {"role": "user", "content": long_text + "\nSummarize this."}
        ]
    )
    print("Success! Context fits.")
except Exception as e:
    print(f"Failed: {e}")
    print("Context too large - reduce prompt or increase max_model_len")
```

### Monitor GPU Memory While Testing

```bash
# Terminal 1: Watch GPU
watch -n1 nvidia-smi

# Terminal 2: Run tests
python3 test_context.py
```

---

## 📋 Implementation Checklist

### ✅ Security (Already Done)

- [x] API key authentication added to all agents
- [x] `.env.example` created
- [x] `SECURITY.md` guide created
- [x] Default API key set (change it!)

### 🎯 Next Steps (For You)

- [ ] Generate your own secure API key
- [ ] Create `.env` file with your key
- [ ] Decide on context length needed
- [ ] Update `docker-compose.yml` if needed
- [ ] Test with authentication
- [ ] Update IDE/CLI tools with API key

---

## 🛠️ Common Tasks

### Change API Key

```bash
# Generate new key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
nano .env  # Change VLLM_API_KEY value

# Restart agents
docker compose restart
```

### Increase Context Length

```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Find dev-agent section, change:
--max-model-len 16384  # to your desired value (e.g., 24576)

# Restart
docker compose restart dev-agent

# Wait 60-90s for model reload
```

### Switch to 7B Model for Large Context

```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Find dev-agent section, change:
--model Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ
# to
--model Qwen/Qwen2.5-7B-Instruct-AWQ

# Also increase context:
--max-model-len 49152  # 48k

# Restart
docker compose restart dev-agent
```

---

## 📚 File References

- **SECURITY.md** - Full security documentation
- **UsageGuide.md** - API usage examples
- **README.md** - Quick start guide
- **docker-compose.yml** - Container configuration
- **.env.example** - API key template

---

## 💡 Recommendations

### For Your 16GB GPU Setup:

1. **Keep current config (16k context)** - Most balanced ✅
   - 14B model quality
   - Safe memory usage
   - Fast inference

2. **Or upgrade to 24k context** - More context, slight risk ⚠️
   - Still 14B quality
   - ~95% GPU usage
   - May need to reduce `gpu_memory_utilization` to 0.90

3. **Or switch to 7B for 48k context** - When you need huge contexts 📄
   - Handles full files
   - Slightly less capable
   - Very safe on memory

### For Large Codebases:

Use 7B-Coder with 32k context - best balance of capability and context size.

---

**Created:** 2025-11-02  
**Your Config:** 16GB GPU, 14B models, 16k context  
**Status:** Production ready with API auth ✅
