# Scan Scope

Include:

- `$CODEX_HOME/skills/*/SKILL.md`
- `$CODEX_HOME/skills/*/modes/*.md`
- `$CODEX_HOME/skills/*/references/*.md`
- `$CODEX_HOME/skills/*/scripts/*`
- `$CODEX_HOME/skills/*/assets/*`
- `$CODEX_HOME/skills/*/schemas/*`
- global anchor: `$CODEX_HOME/AGENTS.md`
- project anchors if present: `AGENTS.override.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `PROJECT.md`, `.codex/PROJECT.md`
- core files: `$CODEX_HOME/custom/CORE.md`, `$CODEX_HOME/custom/RESOLVER.md`, `$CODEX_HOME/custom/COMMON.md`
- `$CODEX_HOME/custom/_core/*.md`
- `$CODEX_HOME/custom/KNOWLEDGE/**/*.md`
- the skill registry: `$CODEX_HOME/custom/_core/active-skills.txt`
- lifecycle hooks: `$CODEX_HOME/hooks.json`, `$CODEX_HOME/hooks/*.sh`
- global config only when explicitly in scope: `$CODEX_HOME/config.toml`
- a project's own `KNOWLEDGE/`, `.agents/skills/` and `.codex/config.toml` when the scan targets a project

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
