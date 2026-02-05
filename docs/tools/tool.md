# Tools

Tools are things the agent can do. A tool is a small, machine-readable specification plus an optional Python handler.

## Types of Tools

There are two tool sources:

- Core tools: bundled with the agent source in `src/tools`.
- User tools (public): stored in the Moltpy config tools folder `${HOME}/.moltpy/tools`.

Both sources support nested subfolders and `.json`, `.yml`, `.yaml` tool files.

## Structure

Each tool lives in its own subfolder:

```
src/tools/echo/
  echo.json
  echo.py
```

## Minimal Definition

```json
{
  "tool_name": "browse_web",
  "description": "Search the web and return sources.",
  "tool": {
    "name": "web.search",
    "input_schema": {
      "type": "object",
      "properties": {
        "query": { "type": "string" }
      },
      "required": ["query"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "results": { "type": "array" }
      }
    }
  },
  "runtime": {
    "handler": "tools.web.search:run",
    "timeout_ms": 8000,
    "requires": ["network"]
  },
  "examples": [
    { "input": { "query": "moltpy agent" } }
  ]
}
```

## Loading

Tools are loaded automatically from:

- `src/tools` (core tools)
- `${HOME}/.moltpy/tools` (user tools)

Both locations support nested subfolders. Supported file types: `.json`, `.yml`, `.yaml`.

## Tool Calls (LLM side)

```python
from core.tools import MoltpyTool

tool = MoltpyTool.from_file("src/tools/echo/echo.json")
call = tool.tool_call(text="Hello Moltpy")

# call => {"name": "echo", "arguments": {"text": "Hello Moltpy"}}
```

## Templates

- `src/templates/tool.example.json`
- `src/templates/tool.example.py`
