# Commands

These commands are available in the Moltpy console.

**Overview**

- `help`: Show all commands.
- `status`: Short status.
- `status full`: Detailed status including uptime, paths, and logging.
- `tools`: List all loaded tools.
- `start`: Start or resume the heartbeat.
- `pause`: Pause the heartbeat.
- `resume`: Resume the heartbeat.
- `restart`: Restart the heartbeat.
- `reload`: Reload configuration.
- `stop`: End the run.
- `exit` or `quit`: Exit the console.

**Examples**

```text
status
status full
tools
reload
pause
resume
```

**Notes**

- `stop` ends the run, `exit` and `quit` close the console.
- `status full` also shows log paths and the current environment.
- `tools` lists tool names and descriptions when available.

**Next**

- Usage: `docs/usage/tui.md`
- Configuration: `docs/setup/configuration.md`
- Logs: `docs/usage/logs.md`
