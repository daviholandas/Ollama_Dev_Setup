# VLLM Tool-Calling Setup Guide

This guide explains how to configure and use VLLM's tool-calling features with your three specialized agents. Tool-calling enables agents to interact with IDEs, build systems, and external tools in a structured way.

## 📋 Overview

VLLM provides two key features for tool integration:

| Feature | Purpose | Use Case |
|---------|---------|----------|
| `--enable-auto-tool-choice` | Automatically select appropriate tools | Agent autonomously calls tools without explicit direction |
| `--tool-call-parser` | Parse and validate tool calls | Extract structured tool invocations from model output |

## 🔧 Configuration

### 1. Environment Variables

Add these to your Docker Compose files:

```yaml
environment:
  # Tool-calling features
  - VLLM_ENABLE_AUTO_TOOL_CHOICE=1
  - VLLM_TOOL_PARSER_MODE=json  # or 'xml'
  - VLLM_TOOL_CALL_RETRY=3
  - VLLM_TOOL_TIMEOUT=30
  
  # Existing optimizations
  - VLLM_GPU_MEMORY_UTILIZATION=0.85
  - VLLM_ENABLE_PREFIX_CACHING=1
```

### 2. Command-Line Arguments

Add these flags to your VLLM startup command:

```bash
vllm serve <model> \
  --enable-auto-tool-choice \
  --tool-call-parser json \
  --port 8000
```

## 🎯 Agent-Specific Configurations

### Architect Agent (Port 8000)

**Purpose**: System design tools

```yaml
VLLM_ENABLED_TOOLS="architecture,design,validation"
VLLM_TOOL_RESPONSE_FORMAT="structured"
```

**Recommended Tools**:
- Architecture validation
- Design pattern analysis
- Deployment strategy tools
- Performance analysis

### Developer Agent (Port 8001)

**Purpose**: Code execution and IDE integration

```yaml
VLLM_ENABLED_TOOLS="code_execution,linting,testing,debugging"
VLLM_TOOL_RESPONSE_FORMAT="structured"
```

**Recommended Tools**:
- Code compilation/execution
- Linter integration (ESLint, Pylint, etc.)
- Test runners
- Git operations
- IDE language server integration

### Product Owner Agent (Port 8002)

**Purpose**: Requirements and planning tools

```yaml
VLLM_ENABLED_TOOLS="requirements,planning,estimation"
VLLM_TOOL_RESPONSE_FORMAT="structured"
```

**Recommended Tools**:
- User story generation
- Sprint planning
- Priority calculation
- Roadmap tools

## 🛠️ Tool Definition Format

### JSON Tool Schema

```json
{
  "type": "function",
  "function": {
    "name": "execute_code",
    "description": "Execute code in a specified language",
    "parameters": {
      "type": "object",
      "properties": {
        "language": {
          "type": "string",
          "description": "Programming language (python, javascript, etc.)",
          "enum": ["python", "javascript", "bash", "sql"]
        },
        "code": {
          "type": "string",
          "description": "Code to execute"
        },
        "timeout": {
          "type": "integer",
          "description": "Execution timeout in seconds",
          "default": 30
        }
      },
      "required": ["language", "code"]
    }
  }
}
```

### XML Tool Schema

```xml
<tool>
  <name>execute_code</name>
  <description>Execute code in a specified language</description>
  <parameters>
    <parameter>
      <name>language</name>
      <type>string</type>
      <description>Programming language</description>
      <required>true</required>
    </parameter>
    <parameter>
      <name>code</name>
      <type>string</type>
      <description>Code to execute</description>
      <required>true</required>
    </parameter>
  </parameters>
</tool>
```

## 📡 API Usage

### Making Tool-Calling Requests

```python
import requests
import json

# Example with tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute code safely",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string"},
                    "code": {"type": "string"}
                },
                "required": ["language", "code"]
            }
        }
    }
]

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "architect",
        "messages": [
            {
                "role": "user",
                "content": "Design a microservices architecture and validate it"
            }
        ],
        "tools": tools,
        "tool_choice": "auto"  # Auto-select when needed
    }
)

result = response.json()

# Check for tool calls
if "tool_calls" in result.get("choices", [{}])[0].get("message", {}):
    tool_calls = result["choices"][0]["message"]["tool_calls"]
    for call in tool_calls:
        print(f"Tool: {call['function']['name']}")
        print(f"Args: {call['function']['arguments']}")
```

### Processing Tool Results

```python
# After executing the tool
tool_result = {
    "role": "tool",
    "tool_call_id": tool_call_id,
    "name": tool_name,
    "content": "Tool execution result..."
}

# Send back to model for further processing
follow_up_response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "architect",
        "messages": [
            original_message,
            assistant_message,
            tool_result
        ]
    }
)
```

## 🔌 IDE/Tool Integration Examples

### VSCode Extension Integration

```python
# In your IDE extension handler
def handle_agent_tool_call(tool_name: str, args: dict):
    """Route tool calls from agents to IDE handlers"""
    
    if tool_name == "code_execution":
        return execute_code_in_ide(args["language"], args["code"])
    elif tool_name == "git_operation":
        return execute_git_command(args["command"])
    elif tool_name == "test_runner":
        return run_tests(args["test_file"], args["framework"])
    elif tool_name == "lint_check":
        return run_linter(args["file"], args["linter"])
    # ... more tool handlers
```

### Build System Integration

```python
# Example: Maven, Gradle, or MSBuild integration
def handle_build_tool_call(tool_name: str, args: dict):
    """Execute build commands through IDE tools"""
    
    if tool_name == "build_project":
        return subprocess.run([
            args.get("build_system", "dotnet"),
            "build",
            args.get("project", ".")
        ])
    elif tool_name == "run_tests":
        return subprocess.run([
            args.get("test_runner", "dotnet"),
            "test",
            args.get("test_filter")
        ])
```

## 🚀 Enabling Tool-Calling: Step-by-Step

### Step 1: Update Docker Compose Files

See the updated `docker-compose-architect.yml`, `docker-compose-dev.yml`, and `docker-compose-po.yml` files below.

### Step 2: Define Tools for Each Agent

Create tool definitions for each agent type:

```bash
mkdir -p tools
touch tools/architect-tools.json
touch tools/dev-tools.json
touch tools/po-tools.json
```

### Step 3: Mount Tool Definitions in Docker

```yaml
volumes:
  - ~/.cache/huggingface:/root/.cache/huggingface
  - ./tools:/app/tools
  - ./outputs:/outputs
```

### Step 4: Update Agent Manager

Modify `agent_manager.py` to handle tool calls:

```python
def call_agent_with_tools(self, agent: str, prompt: str, tools: List[Dict]):
    """Call agent with tool definitions"""
    
    port = self.agents[agent]["port"]
    
    response = requests.post(
        f"http://localhost:{port}/v1/chat/completions",
        json={
            "model": agent,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            "tool_choice": "auto"
        }
    )
    
    return response.json()
```

## 📊 Performance Considerations

### Tool-Calling Overhead

| Factor | Impact | Mitigation |
|--------|--------|------------|
| **Large Tool Sets** | Increases token usage | Group related tools; use tool_choice="required" sparingly |
| **Complex Schemas** | Slows parsing | Validate schemas; keep parameters simple |
| **Network Latency** | Delays tool execution | Use localhost; optimize tool handlers |
| **Model Context** | Consumes tokens | Use batching; cache tool schemas |

### Optimization Tips

```yaml
# In your compose file
environment:
  # Enable schema caching
  - VLLM_ENABLE_SCHEMA_CACHE=1
  
  # Limit concurrent tool calls
  - VLLM_MAX_PARALLEL_TOOL_CALLS=3
  
  # Set reasonable timeouts
  - VLLM_TOOL_TIMEOUT=30
  
  # Cache tool definitions
  - VLLM_CACHE_TOOL_DEFINITIONS=1
```

## 🐛 Troubleshooting

### Tool Calls Not Working

**Problem**: Model ignores tool definitions

```bash
# Check VLLM logs
docker logs vllm-architect-agent | grep -i "tool"

# Verify tool schema is valid
python -m json.tool tools/architect-tools.json
```

**Solution**: Ensure tool schema is valid JSON and matches VLLM expected format

### Tool Call Parsing Failures

**Problem**: "Failed to parse tool call"

```bash
# Check model compatibility
# Not all models support tool-calling (requires specific training)
# Recommended models:
# - Qwen2.5-32B-Instruct-AWQ (supports tools)
# - Mistral-Large (supports tools)
# - GPT-4 compatible quantized models
```

### Timeout Issues

**Problem**: Tool execution times out

```yaml
# Increase timeout in environment
environment:
  - VLLM_TOOL_TIMEOUT=60  # seconds
```

## 📚 Reference

### VLLM Documentation Links

- [VLLM Tool Calling Docs](https://docs.vllm.ai/en/latest/features/tool_call.html)
- [OpenAI Function Calling Format](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema Specification](https://json-schema.org/)

### Model Compatibility

**Models with Tool-Calling Support**:
- ✅ Qwen2.5-32B-Instruct-AWQ
- ✅ Mistral-Large-Instruct
- ✅ LLaMA-2-70B-Chat
- ✅ DeepSeek-Coder-67B-Instruct
- ⚠️ Verify model card for specific model

## 🎓 Best Practices

1. **Keep Tools Focused**: Define one tool per action; avoid bloated tool schemas
2. **Clear Descriptions**: Use detailed, unambiguous tool descriptions
3. **Validation**: Always validate tool arguments before execution
4. **Error Handling**: Return meaningful errors when tools fail
5. **Retry Logic**: Implement automatic retry for transient failures
6. **Monitoring**: Log all tool calls for debugging and analysis
7. **Security**: Sandbox tool execution; validate inputs strictly
8. **Versioning**: Track tool schema versions for compatibility

## 🔄 Next Steps

1. Update your Docker Compose files with tool-calling flags
2. Define tool schemas for each agent
3. Implement tool handlers in your IDE/build system
4. Update `agent_manager.py` to route tool calls
5. Test tool-calling with sample prompts
6. Monitor and optimize based on usage patterns
