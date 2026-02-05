from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MoltpyTool:
    tool_name: str
    description: str
    tool: dict[str, Any]
    runtime: dict[str, Any] = field(default_factory=dict)
    examples: list[dict[str, Any]] = field(default_factory=list)

    @staticmethod
    def _load_file(path: Path) -> dict[str, Any]:
        suffix = path.suffix.lower()
        if suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        if suffix in {".yml", ".yaml"}:
            try:
                import yaml
            except ImportError as exc:
                raise ValueError("PyYAML is required to load YAML tool files.") from exc
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        raise ValueError("Only JSON or YAML tool files are supported.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MoltpyTool":
        if not isinstance(data, dict):
            raise TypeError("Tool data must be a dict.")

        required_fields = ["tool_name", "description", "tool"]
        missing = [key for key in required_fields if key not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        tool = data["tool"]
        if not isinstance(tool, dict) or "name" not in tool:
            raise ValueError("tool must be a dict with at least a 'name' field.")

        return cls(
            tool_name=data["tool_name"],
            description=data["description"],
            tool=tool,
            runtime=data.get("runtime", {}),
            examples=data.get("examples", []),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "MoltpyTool":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Tool file not found: {path}")

        data = cls._load_file(path)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "description": self.description,
            "tool": self.tool,
            "runtime": self.runtime,
            "examples": self.examples,
        }

    def tool_call(self, **kwargs: Any) -> dict[str, Any]:
        input_schema = self.tool.get("input_schema", {})
        required = input_schema.get("required", [])
        missing = [key for key in required if key not in kwargs]
        if missing:
            raise ValueError(f"Missing required inputs: {', '.join(missing)}")

        return {
            "name": self.tool.get("name", self.tool_name),
            "arguments": kwargs,
        }
