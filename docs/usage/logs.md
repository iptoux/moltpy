# Logs

Moltpy can write logs to files so you can track history and status.

**Location**

Default:

- `C:\Users\<Name>\.moltpy\logs\moltpy.log`

If you set a custom path in configuration, that path is used.

**Rotation**

- With size-based rotation, old logs are renamed and archived.
- Example: `moltpy.log.1`, `moltpy.log.2`, etc.

**What is logged**

- Start and end of a run
- Status messages and heartbeat
- Configuration reloads
- Warnings and errors

**Next**

- Configuration: `docs/setup/configuration.md`
- Troubleshooting: `docs/troubleshooting.md`
- Commands: `docs/usage/commands.md`
