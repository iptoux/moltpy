# Installation

This guide describes local installation on Windows.

**Requirements**

- Python 3.13 or newer
- Command line access (PowerShell recommended)

**Steps**

1. Create a virtual environment:

```powershell
python -m venv .venv
```

2. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

**Notes**

- If activation is blocked, allow running local scripts for your session and try again.
- The installation does not create global files.

**Next**

- Quickstart: `docs/setup/quickstart.md`
- Configuration: `docs/setup/configuration.md`
- Usage: `docs/usage/tui.md`
