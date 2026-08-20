# Skill Audit Rules

## Frontmatter

Critical:

- Missing YAML frontmatter.
- Missing `name`.
- Missing `description`.
- Folder name differs from `name`.
- Unsupported frontmatter fields such as `allowed-tools`, `context`, `agent`, `metadata` or `tags`.

## Atomicity

Critical:

- Operational workflow requires reading a sibling skill folder.
- Required reference path points outside the skill folder.
- Missing required local reference.

Warning:

- Optional cross-skill suggestion is not marked optional.
- Shared rule duplication is long and could be moved into a local reference.

## File Surface

Critical:

- `agents/openai.yaml` exists.
- `SKILL.md` exceeds 500 lines.
- Broken relative link to required file.

Warning:

- `SKILL.md` exceeds 300 lines.
- Reference file exceeds 200 lines and lacks a table of contents.
- Script exists but is not executable when it is a shell script.

## Content

Critical:

- Stale required path to removed `_ai/` source.
- `TODO` or `TBD` in operational instructions.

Info:

- Historical migration note references old paths but does not affect execution.
