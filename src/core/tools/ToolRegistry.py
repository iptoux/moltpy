from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .MoltpyTool import MoltpyTool


@dataclass
class MoltpyToolRegistry:
    tools: dict[str, MoltpyTool] = field(default_factory=dict)

    def load_tools(self, paths: Iterable[str | Path]) -> "MoltpyToolRegistry":
        for base in paths:
            base_path = Path(base)
            if not base_path.exists():
                continue

            if base_path.is_file() and base_path.suffix.lower() in {".json", ".yml", ".yaml"}:
                tool = MoltpyTool.from_file(base_path)
                self.tools[tool.tool_name] = tool
                continue

            for file_path in base_path.rglob("*"):
                if file_path.suffix.lower() not in {".json", ".yml", ".yaml"}:
                    continue
                tool = MoltpyTool.from_file(file_path)
                self.tools[tool.tool_name] = tool

        return self

    def get(self, tool_name: str) -> MoltpyTool | None:
        return self.tools.get(tool_name)

    def all(self) -> list[MoltpyTool]:
        return list(self.tools.values())
