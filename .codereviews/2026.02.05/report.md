PRIORITY REVIEW (highest impact first)

P0 — Critical (must fix immediately)
- None observed in current codebase.

P1 — High
- Non-thread-safe logging/rotation can corrupt logs or throw during concurrent writes (Area: Reliability)
  Impact: Heartbeat thread + TUI thread can write/rotate simultaneously; log file can be truncated, interleaved, or raise OSError mid-write, degrading observability and stability.
  Evidence: src/core/Logger.py (class-level `_sinks` list, no locking); src/core/bootstrap/Runtime.py (file_sink + rotate_logs called per write, no lock).
  Fix: add a `threading.Lock` protecting sink writes and rotation; consider `logging` module with `RotatingFileHandler` or a queue-based logger to serialize writes.
  Effort: M
  Risk: Med
- Startup fragile to a single bad tool file (Area: Reliability)
  Impact: One malformed JSON/YAML tool file prevents the entire runtime from initializing.
  Evidence: src/core/tools/ToolRegistry.py `load_tools()` calls `MoltpyTool.from_file()` without try/except.
  Fix: wrap each tool load in try/except; log error and continue; optionally quarantine invalid tools.
  Effort: S
  Risk: Low
- Package/import correctness issues for memory modules (Area: Reliability/Refactor)
  Impact: Running as an installed package or from non-repo CWD will fail due to absolute `src.` imports.
  Evidence: src/core/memory/Memory.py `from src.core.memory.Notes...`; src/core/memory/Notes.py `from src.core.Types...`.
  Fix: convert to package-relative imports (e.g., `from ..Types import Note, NoteType`); ensure `src` is package root.
  Effort: S
  Risk: Low

P1 — High
- Unhandled JSON parse failures in config/env paths (Area: Reliability)
  Impact: Corrupted `config.json` or `CONFIG_PATH` file hard-crashes startup or reload.
  Evidence: src/core/bootstrap/Runtime.py `configObject()` and `envObject()` load JSON without try/except.
  Fix: catch `JSONDecodeError` and `OSError`, log a clear error, fall back to defaults; optionally validate with schema.
  Effort: S
  Risk: Low

P2 — Medium
- Log format doubles timestamps/levels and inflates log size (Area: Maintainability/Perf)
  Impact: Log files become noisy and larger; makes parsing harder and rotation more frequent.
  Evidence: src/core/Logger.py passes a pre-formatted line into sinks; src/core/bootstrap/Runtime.py `file_sink` rewraps with `log_format`.
  Fix: pass structured fields to sinks or have sinks format raw message only once; consider making `file_sink` accept already-rendered lines.
  Effort: S
  Risk: Low
- Heartbeat can spam logs at high frequency (Area: Performance/Reliability)
  Impact: Default heartbeat interval is 0.1s; each cycle logs, which can flood disk/CPU if config isn’t set.
  Evidence: src/core/heartbeat/Heartbeat.py `interval=0.1` and `run_cycle()` logs every cycle.
  Fix: raise default interval to a safer value, or make logging rate-limited; log only on state changes.
  Effort: S
  Risk: Low
- Tool YAML support is declared but dependency missing (Area: Reliability/Dependency)
  Impact: YAML tool files fail at runtime with ImportError.
  Evidence: src/core/tools/MoltpyTool.py imports `yaml` if needed; `requirements.txt` lacks PyYAML.
  Fix: add `PyYAML` pinned version or remove YAML support.
  Effort: S
  Risk: Low
- Configurable log file path can write outside base directory (Area: Security/Config)
  Impact: If config is tampered, log path can overwrite arbitrary files.
  Evidence: src/core/bootstrap/Runtime.py `log_file` can be absolute; `log_path` used directly.
  Fix: restrict to base log dir unless explicitly whitelisted; validate path is within `base_path/logs`.
  Effort: S
  Risk: Low
- `MoltpyMemory.get_notes` return type is incorrect (Area: Correctness)
  Impact: Type mismatch can cause downstream errors if callers expect `MoltpyNotes`.
  Evidence: src/core/memory/Memory.py `def get_notes(self) -> MoltpyNotes:` returns `note_get_all()` (list).
  Fix: return the `MoltpyNotes` instance or change return type to list[Note].
  Effort: S
  Risk: Low

P2 — Medium
- Tool loading lacks schema validation beyond minimal fields (Area: Reliability/Refactor)
  Impact: Partially-valid tool files may lead to errors later if runtime expects more fields.
  Evidence: src/core/tools/MoltpyTool.py only checks `tool_name`, `description`, `tool.name`.
  Fix: validate against a JSON schema; log precise validation errors.
  Effort: M
  Risk: Low
- Missing graceful shutdown behavior for logger sinks (Area: Reliability)
  Impact: File sink remains registered across runtime reinitializations; possible duplicate logs.
  Evidence: src/core/bootstrap/Runtime.py `shutdown()` doesn’t remove sinks.
  Fix: remove file sink on shutdown or ensure singleton logger lifecycle is bounded.
  Effort: S
  Risk: Low

P3 — Low / Nice-to-have
- No test suite or CI checks (Area: Code Quality/Testing)
  Impact: Regressions likely; hard to refactor safely.
  Evidence: No `tests/` directory; no CI configs.
  Fix: add unit tests for tool loading, config parsing, logging, heartbeat state; add CI for lint/type/test.
  Effort: M
  Risk: Low
- No static analysis/security tooling (Area: Security/Quality)
  Impact: Dependency CVEs and risky patterns may go undetected.
  Evidence: No `pyproject.toml` or tooling config.
  Fix: add `ruff`, `mypy` or `pyright`, `bandit`, `pip-audit`; add `requirements` hash-lock or `uv` lock.
  Effort: M
  Risk: Low
- Encoding issues in README and profile metadata (Area: Maintainability)
  Impact: Garbled documentation text; poor UX.
  Evidence: README.md and moltpy.json show broken umlauts.
  Fix: ensure UTF-8 encoding and correct source text.
  Effort: S
  Risk: Low
