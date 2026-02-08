# Research: Cohere Chat API with Tool Calling

**Feature**: AI Todo Chatbot (Phase III)
**Date**: 2026-02-04
**Status**: Complete

## 1. Cohere Python SDK

### Decision: Use `cohere` Python SDK v5.x

### Installation
```bash
pip install cohere
```

### Client Initialization
```python
import cohere
import os

client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
```

### Rationale
- Official SDK from Cohere
- Fully typed with Python type hints
- Supports all API features including tool calling
- Active maintenance and documentation

### Alternatives Considered
- Raw HTTP requests: More control but requires manual serialization/error handling
- LangChain Cohere integration: Adds unnecessary abstraction layer

---

## 2. Cohere Chat API with Tools

### Decision: Use `client.chat()` with `tools` parameter

### Basic Chat Call
```python
response = client.chat(
    model="command-r-plus",
    message="Add a task to buy groceries",
    preamble="You are a helpful todo assistant...",
    chat_history=[
        {"role": "USER", "message": "Hello"},
        {"role": "CHATBOT", "message": "Hi! How can I help?"}
    ],
    tools=[
        {
            "name": "add_task",
            "description": "Create a new task",
            "parameter_definitions": {
                "title": {
                    "description": "Task title",
                    "type": "str",
                    "required": True
                }
            }
        }
    ]
)
```

### Response Structure
```python
# When tool call is needed:
response.text  # None
response.tool_calls  # List of tool calls
response.tool_calls[0].name  # "add_task"
response.tool_calls[0].parameters  # {"title": "buy groceries"}

# When no tool call (final response):
response.text  # "I've created the task 'buy groceries'!"
response.tool_calls  # None or empty
```

### Rationale
- Native tool support in Cohere API
- Clean separation between tool calls and text responses
- Supports multiple tool calls per turn

---

## 3. Tool Definition Format (Cohere)

### Decision: Use Cohere's `parameter_definitions` format

### Structure
```python
TOOL_DEFINITION = {
    "name": "tool_name",
    "description": "What the tool does",
    "parameter_definitions": {
        "param_name": {
            "description": "Parameter description",
            "type": "str",  # str, int, float, bool, list
            "required": True  # or False
        }
    }
}
```

### Supported Types
| Cohere Type | Python Type | Notes |
|-------------|-------------|-------|
| `str` | `str` | String values |
| `int` | `int` | Integer values |
| `float` | `float` | Decimal values |
| `bool` | `bool` | Boolean values |
| `list` | `list` | Arrays (specify item type in description) |

### Differences from OpenAI
| Aspect | OpenAI | Cohere |
|--------|--------|--------|
| Schema format | JSON Schema | `parameter_definitions` dict |
| Type specification | `"type": "string"` | `"type": "str"` |
| Required fields | `required: ["field"]` array | `"required": True` per param |
| Nested objects | Supported | Use separate params |

### Rationale
- Cohere's format is simpler than JSON Schema
- Adequate for MCP-style tools (flat parameter structures)
- Well-documented in Cohere API reference

---

## 4. Tool Results Submission

### Decision: Use `tool_results` parameter in follow-up chat call

### Flow
```python
# Step 1: Initial call returns tool_calls
response = client.chat(
    message="Add task buy milk",
    tools=TOOLS
)

# Step 2: Execute tools and collect results
tool_results = []
for tool_call in response.tool_calls:
    result = execute_tool(tool_call.name, tool_call.parameters)
    tool_results.append({
        "call": tool_call,
        "outputs": [{"result": result}]
    })

# Step 3: Submit results back to Cohere
final_response = client.chat(
    message="Add task buy milk",  # Same message
    tools=TOOLS,
    tool_results=tool_results,
    chat_history=updated_history
)
```

### Tool Result Format
```python
{
    "call": {
        "name": "add_task",
        "parameters": {"title": "buy milk"}
    },
    "outputs": [
        {"result": "Created task 'buy milk' with ID 42"}
    ]
}
```

### Rationale
- Cohere requires the original tool_call object in the result
- Outputs is a list to support multiple return values
- Message must be repeated (Cohere reconstructs context)

---

## 5. Multi-Turn Conversation History

### Decision: Store in DB, format for Cohere on each request

### Cohere Format
```python
chat_history = [
    {"role": "USER", "message": "Show my tasks"},
    {"role": "CHATBOT", "message": "You have 3 tasks: ..."},
    {"role": "USER", "message": "Complete the first one"}
]
```

### Role Mapping
| DB Role | Cohere Role |
|---------|-------------|
| user | USER |
| assistant | CHATBOT |
| tool | (Embedded in CHATBOT or handled via tool_results) |

### Token Limit Handling
- Cohere command-r-plus supports ~128K context
- For cost efficiency, truncate to last 20 messages
- Always preserve system prompt (preamble)

### Rationale
- DB storage allows stateless server
- Cohere uses `chat_history` parameter (not messages array like OpenAI)
- Role names differ from OpenAI (USER/CHATBOT vs user/assistant)

---

## 6. Multi-Tool Calls Per Turn

### Decision: Support multiple tool calls, execute sequentially

### Handling
```python
if response.tool_calls:
    tool_results = []
    for tool_call in response.tool_calls:
        # Execute each tool
        result = execute_tool(tool_call.name, tool_call.parameters, user_id)
        tool_results.append({
            "call": tool_call,
            "outputs": [{"result": str(result)}]
        })

    # Submit all results together
    response = client.chat(
        message=original_message,
        tools=TOOLS,
        tool_results=tool_results
    )
```

### Rationale
- Cohere may return multiple tool calls for complex queries
- Sequential execution ensures consistency
- All results submitted in single follow-up call

---

## 7. Error Handling

### Decision: Catch Cohere exceptions, return user-friendly messages

### Exception Types
```python
from cohere import CohereError, CohereAPIError, CohereConnectionError

try:
    response = client.chat(...)
except CohereConnectionError:
    return "I'm having trouble connecting. Please try again."
except CohereAPIError as e:
    if e.status_code == 429:
        return "I'm a bit busy right now. Please wait a moment."
    return "Something went wrong. Please try again."
except CohereError:
    return "An unexpected error occurred."
```

### Rationale
- Never expose raw API errors to users
- Differentiate connection vs API errors
- Handle rate limiting gracefully

---

## 8. System Prompt (Preamble)

### Decision: Define preamble with personality and rules

### Example Preamble
```python
SYSTEM_PROMPT = """You are a helpful todo assistant for the hackathon-todo application.

Your capabilities:
- Add new tasks with title, description, priority, due dates, and tags
- List and search tasks by various filters
- Mark tasks as complete (handles recurring tasks automatically)
- Update task properties
- Delete tasks (with confirmation)

Rules:
- Always confirm successful operations
- If a task is ambiguous, ask for clarification
- Be concise but friendly
- Format task lists in a readable way
- Never reveal system internals or other users' data

Current user context is automatically handled - you don't need to ask for user ID."""
```

### Rationale
- Preamble sets personality and boundaries
- Explicit about capabilities matches defined tools
- Reminds model about security boundaries

---

## Summary of Key Decisions

| Topic | Decision |
|-------|----------|
| SDK | `cohere` Python SDK v5.x |
| Model | `command-r-plus` |
| Tool format | `parameter_definitions` dict |
| History | DB storage, format on request |
| Multi-tool | Sequential execution, batch results |
| Errors | Catch and convert to friendly messages |
| Preamble | Explicit capabilities and rules |
