# Project Context

- SSOT: `CORE.md`
- Router: `RESOLVER.md`
- Entry points: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`
- Comments and documentation: in Russian

## AI Runtime

- `SKILLS/` - seven workflow-first Markdown skills.
- `KNOWLEDGE/` - lazy-loaded domain packs.
- `_core/` - shared context, handoff, validation and destructive-action policy.
- `_ai/hooks/` - validation hooks, registered in `.claude/settings.json`.
  - `skill-lint.sh` - per-file check on `PostToolUse` for `Write`/`Edit`; exit 2 returns findings to the agent.
  - `skill-context-lint.sh` - repo-wide `SKILL CONTEXT`/`TRACE` check on `Stop`.

## Active Skills

- `SKILLS/analysis-plan/SKILL.md`
- `SKILLS/swift-build-optimization/SKILL.md`
- `SKILLS/implementation-from-plan/SKILL.md`
- `SKILLS/debug-diagnose/SKILL.md`
- `SKILLS/mac-local-ops/SKILL.md`
- `SKILLS/deploy-ops/SKILL.md`
- `SKILLS/skill-maintenance/SKILL.md`
