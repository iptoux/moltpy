# Configuration

Moltpy reads its settings from a profile file and a configuration file.

**Profile: `moltpy.json`**

This contains the base information for the agent.

Example:

```json
{
  "name": "Moltpy",
  "kurzbeschereibung": "Autonomous AI-Agent",
  "beschreibung": "AI-Agent/Bot fuer das Moltpy-Projekt.",
  "aufgabe": "Supports development, automation, and runtime tasks.",
  "geburtsdatum": "2026-02-04",
  "owner": "Maik Roland Damm",
  "contact": "maik@example.com",
  "override": {
    "moltpy_path": "./.moltpy"
  }
}
```

User-relevant fields:

- `name` and `kurzbeschereibung` appear in the console header.
- `override.moltpy_path` sets the storage location for configuration, data, and logs.

**Configuration: `config.json`**

The default configuration lives in the Moltpy data directory. Default path:

- Windows: `C:\Users\<Name>\.moltpy\config.json`

Example:

```json
{
  "runtime": {
    "heartbeat_interval": 5.0,
    "enable_repl": true
  },
  "logging": {
    "log_enabled": true,
    "log_file": "moltpy.log",
    "log_level": "INFO",
    "log_format": "[{asctime}] [{levelname}] {message}",
    "log_date_format": "%Y-%m-%d %H:%M:%S",
    "log_split": "size",
    "log_max_bytes": 1048576,
    "log_backup_count": 5
  }
}
```

Explanations (user-oriented):

- `runtime.heartbeat_interval`: How often the internal status updates.
- `runtime.enable_repl`: Enables or disables interactive input in the console.
- `logging.log_enabled`: Turns file logging on or off.
- `logging.log_file`: Log file name.
- `logging.log_level`: Log verbosity.
- `logging.log_split`: Log rotation ("size" = size-based).
- `logging.log_max_bytes`: Maximum log size before rotation.
- `logging.log_backup_count`: Number of rotated log files to keep.

**Environment variables**

- `APP_ENV`: Sets the environment label (e.g. `dev`, `prod`).
- `CONFIG_PATH`: Alternate path to a configuration file.

**Data**

- User data is stored in `data.json` inside the Moltpy data directory.

**Next**

- Logs: `docs/usage/logs.md`
- Commands: `docs/usage/commands.md`
- Troubleshooting: `docs/troubleshooting.md`
