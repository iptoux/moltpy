# Moltpy

<p align="left">
  <img src="https://img.shields.io/badge/python-3.13%2B-blue?logo=python&logoColor=white" alt="Python 3.13+" />
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/TUI-Rich-1f6feb?logo=terminal&logoColor=white" alt="Rich TUI" />
</p>

Moltpy is a self-contained AI agent that bundles everything needed to run and operate it: a dedicated runtime, a Rich-powered TUI for interactive control, configuration and data management, structured logging with rotation, a heartbeat loop for continuous status updates, and a modular tool system that can be extended with new capabilities.

## ✨ Features

- Rich-based TUI with command input, history, and scrolling output
- Heartbeat loop in a background thread for status updates
- Tool discovery from `src/tools` and the user data directory
- Reloadable `config.json` and profile-based setup via `moltpy.json`
- Logging with rotation and Rich-aware sinks
- Optional CPU/MEM stats in `status full` (via `psutil`)

## ⚡ Quickstart (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\moltpy.py
```

After starting, the console opens. Use `help` to list commands.

## 📚 Documentation

- Start here: `docs/index.md`
- Installation: `docs/setup/installation.md`
- Quickstart: `docs/setup/quickstart.md`
- Configuration: `docs/setup/configuration.md`
- TUI usage: `docs/usage/tui.md`
- Commands: `docs/usage/commands.md`
- Logs: `docs/usage/logs.md`

## 🧩 Project Layout

- Entry point: `src/moltpy.py`
- Runtime singleton: `src/core/bootstrap/Runtime.py`
- Heartbeat loop: `src/core/heartbeat/Heartbeat.py`
- TUI: `src/tui/Tui.py`
- Tool system: `src/core/tools/` and `src/tools/`
- Agent profile: `moltpy.json`

## 🔧 Configuration

- Profile: `moltpy.json` (basic agent metadata and optional `override.moltpy_path`)
- Runtime config: `config.json` in the Moltpy data directory (default: `~/.moltpy/config.json`)
- Reload config at runtime via the `reload` command in the TUI
