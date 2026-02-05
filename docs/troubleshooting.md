# Troubleshooting

**Moltpy does not start**

- Check that the virtual environment is active.
- Check that `moltpy.json` exists in the project folder.
- Read the log file in the Moltpy data directory.

**Configuration changes are not applied**

- Run `reload` in the console.
- Ensure the JSON file is valid.

**No logs are visible**

- Set `logging.log_enabled` to `true`.
- Check the path in `logging.log_file`.

**Status shows no CPU/MEM**

- If no system stats appear, the system module is not available.
- Restart Moltpy after installing dependencies.

**Next**

- Logs: `docs/usage/logs.md`
- Configuration: `docs/setup/configuration.md`
- FAQ: `docs/faq.md`
