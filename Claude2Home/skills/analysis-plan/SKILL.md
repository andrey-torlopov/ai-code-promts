---
name: analysis-plan
description: Produces analysis, plans, reviews, research reports, repository scouts, dependency reports and specs without implementation. Use when the deliverable is a Markdown artifact or findings rather than code changes.
---

# Analysis Plan

Skill root: `~/.claude/skills/analysis-plan/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

This skill is read-only except for explicitly requested Markdown artifacts.

## SKILL CONTEXT

Before substantial work, output the block from `~/.claude/custom/_core/skill-context.md`.
Set `mode` to one of:

- `plan`
- `refactor`
- `architecture`
- `scout`
- `deps`
- `review`
- `research`
- `spec`

## Inputs

- User goal and concrete deliverable.
- Scope: repository, module, files, diff, logs, product idea or research question.
- Optional output path for a Markdown artifact.
- Optional acceptance criteria, exclusions and recency requirements.

## Workflow

1. Read `~/.claude/custom/RESOLVER.md` only if the mode is not already clear.
2. Read the selected `modes/<mode>.md`.
3. Read only the references named by that mode.
4. Load only the minimum `~/.claude/custom/KNOWLEDGE/` packs selected by the mode and scope.
5. Inspect real files, diffs or sources before making claims.
6. Separate confirmed facts from assumptions and blockers.
7. Produce findings, plan, report or spec in the mode-specific format.
8. Stop at the analysis deliverable.

## Local References

- `references/evidence-rules.md`
- `references/output-format.md`
- `references/handoff-to-implementation.md`

Mode files name additional local references.

## Output

Return or write the requested artifact. For reviews, findings come first and summaries are secondary.

For substantial work, finish with `TRACE` from `~/.claude/custom/_core/skill-context.md`.

## Stop Conditions

- Do not edit production code or project configuration.
- Do not run implementation, deployment or release steps.
- Do not require another skill folder.
- If the user asks for code changes and no approved plan or concrete directive exists, stop with an implementation handoff.
