# Scan Scope

Include:

- `~/.claude/skills/*/SKILL.md`
- `~/.claude/skills/*/references/*.md`
- `~/.claude/skills/*/scripts/*`
- `~/.claude/skills/*/assets/*`
- global anchors: `~/.claude/CLAUDE.md`, `~/.claude/custom/AGENTS.md`, `~/.claude/custom/GEMINI.md`
- project anchors if present: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `PROJECT.md`
- core files: `~/.claude/custom/CORE.md`, `~/.claude/custom/RESOLVER.md`, `~/.claude/custom/COMMON.md`
- `~/.claude/custom/_core/*.md`
- `~/.claude/custom/KNOWLEDGE/**/*.md`
- the skill registry: `~/.claude/custom/_core/active-skills.txt`
- global config: `~/.claude/settings.json`
- validation hooks: `~/.claude/hooks/*.sh`
- a project's own `KNOWLEDGE/` and `.claude/skills/` when the scan targets a project

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
