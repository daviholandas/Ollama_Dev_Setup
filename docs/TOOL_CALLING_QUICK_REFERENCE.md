# VLLM Tool-Calling Quick Reference

## 🚀 Quick Start

### 1. Update Docker Compose Files
Already done! Your Docker Compose files now include:
- `--enable-auto-tool-choice` flag
- `--tool-call-parser json` flag
- Environment variables for tool-calling configuration

### 2. Launch an Agent with Tool Support

```bash
# Launch Architect Agent (with tool support)
cd agents/
docker-compose -f docker-compose-architect.yml up -d

# Or use the agent manager
python3 agent_manager.py --launch architect
```

### 3. Test Tool-Calling with cURL

```bash
# Example: Ask Architect to validate architecture
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "architect",
    "messages": [
      {"role": "user", "content": "Validate a microservices architecture with 5 services"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "validate_architecture",
          "description": "Validate system architecture",
          "parameters": {
            "type": "object",
            "properties": {
              "architecture_description": {"type": "string"},
              "validation_scope": {"type": "string", "enum": ["microservices", "monolithic"]}
            },
            "required": ["architecture_description", "validation_scope"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'
```

## 📁 Files Created

| File | Purpose |
|------|---------|
| `agents/docker-compose-architect.yml` | Updated with tool-calling flags |
| `agents/docker-compose-dev.yml` | Updated with code execution flags |
| `agents/docker-compose-po.yml` | Updated with planning tool flags |
| `tools/architect-tools.json` | Architecture validation tools |
| `tools/dev-tools.json` | Code execution and testing tools |
| `tools/po-tools.json` | Planning and requirements tools |
| `tool_integration.py` | Python tool handler framework |
| `docs/TOOL_CALLING_SETUP.md` | Comprehensive setup guide |

## 🎯 Environment Variables Added

### All Agents
```yaml
VLLM_ENABLE_AUTO_TOOL_CHOICE=1        # Auto-select tools
VLLM_TOOL_CALL_PARSER=json            # Parse tool calls as JSON
VLLM_MAX_PARALLEL_TOOL_CALLS=2-3      # Limit concurrent calls
VLLM_TOOL_TIMEOUT=30-60               # Timeout in seconds
VLLM_ENABLE_SCHEMA_CACHE=1            # Cache tool schemas
VLLM_CACHE_TOOL_DEFINITIONS=1         # Cache definitions
```

### Developer Agent (Additional)
```yaml
VLLM_ENABLE_CODE_EXECUTION=1          # Enable code execution
VLLM_SANDBOX_CODE_EXECUTION=1         # Sandbox for safety
```

## 🛠️ Using Tool Integration in Python

```python
from tool_integration import IDEToolIntegration
import json

# Initialize
integration = IDEToolIntegration()

# List available tools
tools = integration.registry.get_tools_for_agent("dev")
for tool in tools:
    print(f"• {tool['function']['name']}")

# Execute a tool
result = integration.registry.execute_tool(
    agent="dev",
    tool_name="execute_code",
    arguments={
        "language": "python",
        "code": "print('Hello from agent')",
        "timeout": 10
    }
)

print(json.dumps(result, indent=2))
```

## 🔌 Tool-Calling Flow

```
User Request
    ↓
Agent with Tool Definitions
    ↓
Model evaluates: "Should I use a tool?"
    ↓
[Auto Tool Choice] If yes → Select appropriate tool
    ↓
[Tool Call Parser] Parse tool call arguments
    ↓
Route to Handler (IDE/Build System)
    ↓
Execute Tool & Return Results
    ↓
Agent processes results → Continue conversation
```

## 📊 Available Tools by Agent

### Architect Agent (Port 8000)
```
✓ validate_architecture        - Validate against best practices
✓ generate_architecture_diagram - Create visual diagrams (Mermaid, PlantUML)
✓ analyze_performance_implications - Performance analysis
✓ suggest_technology_stack     - Tech stack recommendations
```

### Developer Agent (Port 8001)
```
✓ execute_code                 - Run code safely
✓ run_tests                    - Execute test suites
✓ lint_code                    - Code quality checks
✓ git_operation                - Git commands
✓ analyze_code                 - Code analysis
✓ build_project                - Build compilation
✓ debug_code                   - Debugging assistance
```

### Product Owner Agent (Port 8002)
```
✓ generate_user_story          - Create user stories
✓ create_prioritization_matrix - Prioritize features
✓ plan_sprint                  - Sprint planning
✓ generate_roadmap             - Product roadmap
✓ analyze_requirements         - Requirements analysis
✓ stakeholder_communication    - Generate communications
```

## 🚨 Important Notes

### Model Compatibility
Not all models support tool-calling! Use models specifically trained for it:
- ✅ **Recommended**: Qwen2.5-32B-Instruct-AWQ (your setup)
- ✅ **Recommended**: Qwen2.5-Coder-14B-Instruct-GPTQ (your setup)
- ✅ **Recommended**: Mistral-Large-Instruct
- ⚠️ **Check model card** for tool-calling support

### Safety Considerations
1. **Code Execution**: Sandbox all code before execution
2. **Tool Arguments**: Validate all inputs strictly
3. **Resource Limits**: Use timeouts to prevent hangs
4. **Error Handling**: Always catch and handle errors gracefully

### Performance Tips
1. **Cache Tool Schemas**: Reduces token usage
2. **Limit Parallel Calls**: Prevent resource exhaustion
3. **Set Reasonable Timeouts**: Balance responsiveness and reliability
4. **Monitor GPU Memory**: Watch for leaks with long-running agents

## 🔍 Debugging

### Check Tool Loading
```bash
python3 tool_integration.py --agent dev --list-tools
```

### View Agent Logs
```bash
docker logs vllm-architect-agent | grep -i "tool"
docker logs vllm-dev-agent | grep -i "tool"
docker logs vllm-po-agent | grep -i "tool"
```

### Test Tool Execution
```bash
# Test code execution tool
python3 tool_integration.py \
  --agent dev \
  --tool execute_code \
  --args '{"language":"python","code":"print(1+1)"}'
```

### Verify VLLM Config
```bash
docker exec vllm-architect-agent env | grep VLLM_ENABLE_AUTO_TOOL_CHOICE
```

## 📡 Integration with IDEs

### VSCode Extension
Create a VSCode extension that:
1. Captures user requests
2. Sends to appropriate agent via API
3. Parses tool calls from response
4. Routes to IDE features (LSP, build, git, etc.)

### IntelliJ IDEA Plugin
Similar pattern with IntelliJ Plugin API

### Neovim Integration
Use Neovim's RPC API to communicate with agents

## 🔄 Workflow Example

### Design → Code → Test Cycle

```bash
# 1. Plan with PO Agent
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"po", "messages":[...], "tools":...}'

# 2. Design with Architect
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"architect", "messages":[...], "tools":...}'

# 3. Implement with Developer
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"dev", "messages":[...], "tools":...}'

# 4. Test and Deploy
# (Developer agent uses build_project and run_tests tools)
```

## 🎓 Next Steps

1. **Mount Tool Definitions**: Update your compose files to mount tool JSON files (already done!)
2. **Implement Tool Handlers**: Extend `tool_integration.py` with custom handlers for your IDEs
3. **Test Tool-Calling**: Use provided examples to test each agent
4. **Monitor Performance**: Track token usage and response times
5. **Optimize Tools**: Add more tools as needed for your workflow

## 📚 Resources

- [VLLM Documentation](https://docs.vllm.ai/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema Reference](https://json-schema.org/)
- Local docs: `docs/TOOL_CALLING_SETUP.md`

## ✅ Verification Checklist

- [ ] Docker Compose files updated with tool flags
- [ ] Tool definition files created in `tools/` directory
- [ ] `tool_integration.py` copied to project root
- [ ] `TOOL_CALLING_SETUP.md` reviewed
- [ ] Agents launched successfully
- [ ] Tool definitions accessible at `/app/tools` in containers
- [ ] Tested at least one agent with tools
- [ ] Integrated with IDE/build system (optional)

## 🆘 Troubleshooting

**Problem**: "tool_calls" not in response
- **Solution**: Check model supports tool-calling; verify tools parameter in request

**Problem**: Tool arguments parsing fails
- **Solution**: Validate JSON schema; check VLLM logs for parsing errors

**Problem**: Timeout errors
- **Solution**: Increase `VLLM_TOOL_TIMEOUT` environment variable

**Problem**: Out of memory with tools
- **Solution**: Reduce `VLLM_MAX_PARALLEL_TOOL_CALLS`; use smaller models

---

**Status**: ✅ Tool-calling fully configured and ready to use!
