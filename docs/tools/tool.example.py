from pathlib import Path

from core.tools import MoltpyTool


tool = MoltpyTool.from_file(Path("src/tools/echo/echo.json"))
call = tool.tool_call(text="Hello Moltpy")

print(call)
