# Moltpy Gemini Instructions

Follow these repo-specific conventions.

## Project Overview
- Entry point is `src/moltpy.py`: initializes `MoltpyRuntime` and launches the Rich TUI (`MoltpyTui`). See `src/tui/Tui.py`.
- The runtime is a singleton (`MoltpyRuntime.get_instance()`), responsible for config/data loading, tool discovery, logging setup, and the heartbeat thread. See `src/core/bootstrap/Runtime.py`.
- The heartbeat loop runs in a background thread and drives status updates/logs. See `src/core/heartbeat/Heartbeat.py`.

## Configuration & Data
- Agent profile is `moltpy.json` in repo root; `override.moltpy_path` can relocate the data directory. See `docs/setup/configuration.md`.
- Runtime config is `config.json` inside the Moltpy data directory (default: `~/.moltpy/config.json`); reload via TUI command `reload`.
- Environment variables: `APP_ENV` and optional `CONFIG_PATH` for alternate config. See `src/core/bootstrap/Runtime.py`.

## Tools System
- Tools are defined as JSON/YAML files with `tool_name`, `description`, and a `tool` dict (must include `name`). See `src/core/tools/MoltpyTool.py`.
- Tools are loaded from both the repo (`src/tools`) and the user data directory (`~/.moltpy/tools` or override path). See `src/core/tools/ToolRegistry.py`.
- Example tool: `src/tools/echo/echo.json` with implementation `src/tools/echo/echo.py`.

## Logging & UI
- Logging uses `MoltpyLogger` with Rich-aware sinks; file logging is controlled by `logging.*` config keys and rotation happens in `MoltpyRuntime.configure_logging()`.
- TUI commands are hard-coded in `MoltpyTui.COMMANDS` (e.g., `status full`, `tools`, `reload`, `pause`). See `src/tui/Tui.py` and docs in `docs/usage/commands.md`.
- CPU/MEM stats in `status full` require `psutil` (optional dependency). See `requirements.txt` and `src/tui/Tui.py`.

## Developer Workflows
- Install deps: `python -m venv .venv` then `\.\.venv\Scripts\Activate.ps1` then `pip install -r requirements.txt`.
- Run locally: `python src\moltpy.py`.

## Conventions & Patterns
- Prefer the runtime singleton and logger factory (`MoltpyRuntime.get_instance()`, `MoltpyLogger.for_class(...)`) rather than direct instantiation.
- Keep config/data access through `ConfigObject`/`DataObject` wrappers in `src/core/Types.py`.
- When adding tools, include both the definition file and a corresponding implementation module under `src/tools/<tool>/`.
