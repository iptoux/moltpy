# User Tools (Public)

This directory contains your **public user tools**.

User tools are executable or callable components that you load from your local tools configuration directory:

- `${HOME}/.moltpy/tools`

They extend what you can do by providing concrete, runnable functionality (e.g. scripts, helpers, adapters).

---

## Directory Structure

User tools are organized using **subfolders**, typically by **domain, provider, or package name**.

A tool itself usually lives in its own folder and may consist of multiple files (code, config, metadata).

```
tools/
└─ example.com/
└─ echo/
├─ echo.json
└─ echo.py
```

---

## Tool Files

A tool directory typically contains:

- A **tool definition file** (e.g. `echo.json`)
  - Describes the tool’s name, inputs, outputs, and behavior
- One or more **implementation files** (e.g. `echo.py`)
  - Contains the executable logic

Additional helper or resource files may be included as needed.

---

## Organization Guidelines

- Group tools by **domain or logical owner**
- Keep each tool in its **own folder**
- Avoid mixing unrelated tools in the same directory
- Prefer explicit, readable names over short or clever ones

A clean structure makes tools easier to discover, debug, and maintain.

---

## Loading Behavior

All public user tools are loaded from:

```
${HOME}/.moltpy/tools
```


At startup (or reload), you scan this directory and register all valid tools found within it.

Removing a tool is as simple as deleting its folder.

---

## Trust & Safety Notes

- Only place tools here that you trust to execute
- Treat every tool as executable code
- Do not run tools from unknown or unverified sources
- Domain folders act as **soft trust boundaries**

---

## Summary

- User tools live in `${HOME}/.moltpy/tools`
- Use subfolders to organize by domain or package
- Each tool gets its own folder
- Tools may consist of multiple files
- Keep things explicit, structured, and auditable
