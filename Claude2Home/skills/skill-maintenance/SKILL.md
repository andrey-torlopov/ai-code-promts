---
name: skill-maintenance
description: Creates, updates, audits, lints and registers AI instruction skills and context files. Use for maintaining this Markdown-first instruction system.
---

# Skill Maintenance

Skill root: `~/.claude/skills/skill-maintenance/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

This skill maintains the instruction system itself.

## SKILL CONTEXT

Before substantial work, output the block from `~/.claude/custom/_core/skill-context.md`.
Set `mode` to one of:

- `authoring`
- `audit`
- `lint`
- `registry`
- `ai-context-init`

## Inputs

- Maintenance goal.
- Root or skill path.
- Optional report path.
- Current date when writing changelog entries.
- Permission boundary for creating, updating or deleting instruction files.

## Workflow

1. Read the selected `modes/<mode>.md`.
2. Read only the references/scripts/assets named by that mode.
3. Inspect existing files before changing or judging them.
4. Preserve workflow-first architecture: `~/.claude/custom/CORE.md`, `~/.claude/custom/RESOLVER.md`, registered active workflow skills and lazy `~/.claude/custom/KNOWLEDGE/`.
5. Apply the smallest instruction-system change that satisfies the request.
6. Run focused validation when files changed.
7. Report changed files, validation and residual risk.

## Local References

- `references/skill-contract.md`
- `references/migration-checklist.md`
- `scripts/skill-lint.sh`

Mode files name additional local references.

## Output

Return changed files or audit findings, validation status and final `TRACE`.

## Stop Conditions

- Do not change runtime anchors or routing outside the requested scope.
- Do not add a top-level skill when a mode or `~/.claude/custom/KNOWLEDGE/<domain>/` pack is enough unless the user explicitly requests a skill folder and routing.
- Do not delete active legacy or bridge content without a migration checklist or explicit user permission.
- Do not require another skill folder.
