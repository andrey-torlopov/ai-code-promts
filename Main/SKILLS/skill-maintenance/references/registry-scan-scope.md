# Scan Scope

Include:

- `SKILLS/*/SKILL.md`
- `SKILLS/*/references/*.md`
- `SKILLS/*/scripts/*`
- `SKILLS/*/assets/*`
- root-level runtime anchors if present: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- core files: `CORE.md`, `RESOLVER.md`, `COMMON.md`
- `_core/*.md`
- `KNOWLEDGE/**/*.md`
- prompt-pack files under `Main/` only when the registry is documenting migration state
- validation hooks and local scripts when they are part of the AI setup

Exclude:

- `.git/`
- build output
- dependency folders
- binary files
- generated reports under `audit/` unless the user asks to include reports

For each Markdown file, record:

```text
path:
line-count:
owner:
purpose:
status:
```
