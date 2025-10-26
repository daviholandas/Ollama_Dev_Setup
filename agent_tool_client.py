#!/usr/bin/env python3
"""
agent_tool_client.py - Client for communicating with VLLM agents and handling tool calls

This module provides:
- OpenAI-compatible client for VLLM agents
- Tool call extraction and routing
- Streaming support
- Error handling and retries
"""

import requests
import json
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, asdict
import time


@dataclass
class AgentConfig:
    """Configuration for VLLM agent"""
    name: str
    host: str
    port: int
    model_name: str
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/v1"


class AgentToolClient:
    """Client for communicating with VLLM agents with tool-calling support"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.session = requests.Session()
        self.tool_handlers = {}

    def register_tool_handler(self, tool_name: str, handler: callable):
        """Register a handler for tool calls"""
        self.tool_handlers[tool_name] = handler

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a chat completion request to the agent.
        
        Args:
            messages: List of message dicts with role and content
            tools: List of tool definitions
            tool_choice: How to handle tool calls ("auto", "required", tool name, etc.)
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            stream: Whether to stream response
            **kwargs: Additional parameters to pass to API
            
        Returns:
            Response from agent (dict or generator if streaming)
        """
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        
        payload.update(kwargs)
        
        url = f"{self.config.base_url}/chat/completions"
        
        try:
            response = self.session.post(url, json=payload, timeout=300, stream=stream)
            response.raise_for_status()
            
            if stream:
                return self._stream_response(response)
            else:
                return response.json()
                
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {self.config.name} agent timed out")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Failed to connect to {self.config.name} agent at {url}")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Agent returned error: {e.response.text}")

    def _stream_response(self, response: requests.Response) -> Generator[Dict, None, None]:
        """Stream response from agent"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data != '[DONE]':
                        yield json.loads(data)

    def handle_tool_calls(
        self,
        response: Dict[str, Any],
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Extract and execute tool calls from agent response.
        
        Args:
            response: Response from chat_completion
            max_retries: Max retries for failed tool calls
            
        Returns:
            List of tool results
        """
        results = []
        
        try:
            message = response["choices"][0]["message"]
        except (KeyError, IndexError):
            return results
        
        # Check if there are tool calls
        if "tool_calls" not in message:
            return results
        
        tool_calls = message.get("tool_calls", [])
        
        for tool_call in tool_calls:
            tool_result = self._execute_tool_call(tool_call, max_retries)
            results.append(tool_result)
        
        return results

    def _execute_tool_call(self, tool_call: Dict, max_retries: int) -> Dict[str, Any]:
        """Execute a single tool call with retries"""
        tool_name = tool_call["function"]["name"]
        tool_id = tool_call.get("id", "")
        
        try:
            arguments = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError as e:
            return {
                "tool_call_id": tool_id,
                "tool_name": tool_name,
                "success": False,
                "error": f"Failed to parse tool arguments: {e}"
            }
        
        # Check if we have a handler
        if tool_name not in self.tool_handlers:
            return {
                "tool_call_id": tool_id,
                "tool_name": tool_name,
                "success": False,
                "error": f"No handler registered for tool: {tool_name}"
            }
        
        handler = self.tool_handlers[tool_name]
        
        # Execute with retries
        for attempt in range(max_retries):
            try:
                result = handler(**arguments)
                return {
                    "tool_call_id": tool_id,
                    "tool_name": tool_name,
                    "success": True,
                    "result": result
                }
            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        "tool_call_id": tool_id,
                        "tool_name": tool_name,
                        "success": False,
                        "error": str(e)
                    }
                time.sleep(2 ** attempt)  # Exponential backoff

    def chat_with_tools(
        self,
        user_message: str,
        tools: List[Dict],
        system_message: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        max_iterations: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Multi-turn conversation with automatic tool handling.
        
        Automatically:
        1. Sends user message with tools
        2. Extracts tool calls from response
        3. Executes tools
        4. Adds results to conversation
        5. Gets agent's final response
        
        Args:
            user_message: User's message
            tools: List of tool definitions
            system_message: System prompt (optional)
            conversation_history: Prior conversation (optional)
            tool_choice: Tool selection strategy
            max_iterations: Max tool-calling iterations
            **kwargs: Additional parameters
            
        Returns:
            Final response with all conversation data
        """
        messages = conversation_history or []
        
        if system_message:
            messages.insert(0, {"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        iteration = 0
        final_response = None
        
        while iteration < max_iterations:
            iteration += 1
            
            # Get response from agent
            response = self.chat_completion(
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs
            )
            
            final_response = response
            
            # Check if agent wants to use tools
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            if "tool_calls" not in message:
                # No tool calls - we're done
                break
            
            # Add assistant's response to conversation
            messages.append({
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls", [])
            })
            
            # Execute tool calls
            tool_results = self.handle_tool_calls(response)
            
            # Add tool results to conversation
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "name": result["tool_name"],
                    "content": json.dumps(result)
                })
        
        return {
            "success": True,
            "iterations": iteration,
            "final_response": final_response,
            "conversation": messages
        }

    def close(self):
        """Close session"""
        self.session.close()


# Example usage
def example_architect_workflow():
    """Example: Using Architect agent with tool-calling"""
    
    # Configure architect agent
    architect = AgentConfig(
        name="Architect",
        host="localhost",
        port=8000,
        model_name="architect"
    )
    
    # Create client
    client = AgentToolClient(architect)
    
    # Load tool definitions
    with open("tools/architect-tools.json") as f:
        tools = json.load(f)
    
    # Register tool handlers
    def validate_arch(**kwargs):
        """Mock handler for architecture validation"""
        return {
            "validation_score": 85,
            "issues": [],
            "recommendations": [
                "Add API gateway for routing",
                "Implement circuit breaker pattern"
            ]
        }
    
    def generate_diagram(**kwargs):
        """Mock handler for diagram generation"""
        return {
            "diagram": "Generated Mermaid diagram",
            "format": kwargs.get("diagram_type")
        }
    
    client.register_tool_handler("validate_architecture", validate_arch)
    client.register_tool_handler("generate_architecture_diagram", generate_diagram)
    
    # Multi-turn conversation with tools
    response = client.chat_with_tools(
        user_message="Design a microservices architecture for an e-commerce platform",
        tools=tools,
        system_message="You are a system architect. Use tools to validate and visualize designs.",
        temperature=0.3,
        max_tokens=2048,
        max_iterations=3
    )
    
    print(json.dumps(response, indent=2, default=str))
    client.close()


def example_dev_workflow():
    """Example: Using Developer agent with tool-calling"""
    
    # Configure dev agent
    dev = AgentConfig(
        name="Developer",
        host="localhost",
        port=8001,
        model_name="dev"
    )
    
    # Create client
    client = AgentToolClient(dev)
    
    # Load tool definitions
    with open("tools/dev-tools.json") as f:
        tools = json.load(f)
    
    # Register handlers for code execution
    def execute_code(language: str, code: str, **kwargs) -> Dict:
        """Execute code safely"""
        import subprocess
        try:
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    client.register_tool_handler("execute_code", execute_code)
    
    # Multi-turn with tools
    response = client.chat_with_tools(
        user_message="Write a function to calculate factorial and test it",
        tools=tools,
        system_message="You are an expert developer. Write and test code.",
        temperature=0.2,
        max_tokens=3000,
        max_iterations=5
    )
    
    print(json.dumps(response, indent=2, default=str))
    client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "architect":
        example_architect_workflow()
    elif len(sys.argv) > 1 and sys.argv[1] == "dev":
        example_dev_workflow()
    else:
        print("Usage: python agent_tool_client.py [architect|dev]")
        print("\nExample:")
        print("  python agent_tool_client.py architect")
        print("  python agent_tool_client.py dev")
