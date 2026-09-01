---
name: mac-local-ops
description: Plans and performs safe macOS, shell, filesystem and local diagnostic tasks. Use for file operations, command output, cache checks and non-domain-specific local execution.
---

# Mac Local Operations

Skill root: `~/.claude/skills/mac-local-ops/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

This skill is atomic and must not depend on other skill folders.

## SKILL CONTEXT

Before substantial work, output the SKILL CONTEXT block (the template is already in the
injected RESOLVER.md; fallback: `~/.claude/custom/_core/skill-context.md`).
For shell tasks, show whether `~/.claude/custom/KNOWLEDGE/shell/_rules.md` was loaded.
For destructive work, show the destructive-action gate before executing.

## Inputs

- Local task description.
- Target paths.
- Whether execution is requested or only analysis/planning.

## Workflow

1. Inspect before acting.
2. Read `~/.claude/custom/_core/destructive-actions-policy.md`.
3. Load `~/.claude/custom/KNOWLEDGE/shell/_rules.md` when shell, zsh, mise or brew behavior matters.
4. If the request is unclear, produce a safe plan or ask one narrow question.
5. Prefer inventory and dry-run for file operations.
6. Execute only commands that match the approved task and current sandbox permissions.
7. Verify the result.
8. Report commands run, changed paths and rollback notes.

## References

- `~/.claude/custom/_core/destructive-actions-policy.md` - confirmation gate.
- `references/completion-format.md` - final report format.

## Output

Return command results, changed paths, rollback notes and final `TRACE` for substantial work.

## Stop Conditions

- Do not delete, mass rename, install, uninstall, use `sudo`, change permissions or clear irreversible caches without explicit confirmation.
- Do not treat fallback ownership as permission for unsafe execution.
- Do not handle code review, architecture, implementation or deploy/release work here.
