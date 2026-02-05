## Public Skills

Public Skills are externally hosted skill definitions that you can load at runtime.

All skills fetched from the web **should be stored locally** in this directory, **one subfolder per domain**, to keep origins clearly separated and avoid trust or security issues.

### Directory Structure

Each domain gets its own folder. Inside that folder, store the skill definition files (at minimum `skill.md`):

```
skills/
├─ example.com/
│ └─ skill.md
```

---

## Why Domain-Based Folders Matter

Organizing skills by domain ensures:

- Clear separation of trust boundaries
- No accidental mixing of files from different providers
- Easier auditing, updating, or removal of skills
- Deterministic and reproducible skill loading

Treat the domain folder as the **security boundary** for that skill.

---

## Required Files

### `skill.md`

`skill.md` is the **primary entry point** for every public skill.

It typically defines:

- What the skill does
- Which capabilities it provides
- How you should use it
- Security, behavioral, and usage constraints

You should always read and respect the instructions in `skill.md` before using a skill.

---

## Optional Files

Some skill providers may ship additional files alongside `skill.md`, such as:

- `heartbeat.md` – instructions for periodic or recurring actions
- `messaging.md` – communication or interaction guidelines
- Metadata files (e.g. JSON manifests)

If provided, store these files **next to `skill.md` in the same domain folder**.

---

## Example (Multiple Files)

### Example

```
public-skills/
├─ moltbook.com/
│ ├─ skill.md
│ ├─ heartbeat.md
│ └─ messaging.md
```

## Usage Guidelines

- Only load skills from domains you trust
- Never merge or move files between domain folders
- If a skill is updated, replace the files in its domain folder
- If a skill is removed, delete the entire domain folder

Public skills define **capabilities and constraints** — they are not just documentation.  
You are expected to follow them exactly.

---

## Summary

- One domain = one folder
- `skill.md` is mandatory
- Additional files stay within the same domain folder
- Domain boundaries are security boundaries

Keep this directory clean, explicit, and auditable.


### Purpose

- Clearly separate skills by **origin domain**
- Prevent accidental mixing of files from different providers
- Make it easy to audit, update, or remove a skill
- Enable deterministic skill loading

### Notes

- Folder names **must match the domain** the skill was fetched from
- `skill.md` is the primary entry point and defines:
  - What the skill does
  - How you should use it andn how you should interact and what are your next steps.
  - Security and behavioral constraints
- Additional files (e.g. `heartbeat.md`, `messaging.md`, metadata files) may be stored alongside `skill.md` if provided by the skill author