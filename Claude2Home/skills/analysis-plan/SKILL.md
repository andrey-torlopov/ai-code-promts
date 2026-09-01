---
name: analysis-plan
description: Produces analysis, plans, reviews, research reports, repository scouts, dependency reports and specs without implementation. Use when the deliverable is a Markdown artifact or findings rather than code changes.
---

# Analysis Plan

Skill root: `~/.claude/skills/analysis-plan/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

This skill is read-only except for explicitly requested Markdown artifacts and, with
explicit user consent, visual-companion HTML mockups under a temporary directory
(`references/visual-companion.md`).

## SKILL CONTEXT

Before substantial work, output the SKILL CONTEXT block (the template is already in the
injected RESOLVER.md; fallback: `~/.claude/custom/_core/skill-context.md`).
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

## Knowledge

Load by detected scope, minimum set; `general` is the fallback, never an addition:

- Swift or `.swift`: `~/.claude/custom/KNOWLEDGE/swift/_rules.md`
- Swift patterns, only on a concrete signal: `~/.claude/custom/KNOWLEDGE/swift/patterns/` (entry: `patterns/_summary-index.md`)
- iOS or Xcode app structure: `~/.claude/custom/KNOWLEDGE/ios/_rules.md`
- CI, pipeline or deployment scope: `~/.claude/custom/KNOWLEDGE/devops/_rules.md`
- Shell scripts: `~/.claude/custom/KNOWLEDGE/shell/_rules.md`
- Python: `~/.claude/custom/KNOWLEDGE/python/_rules.md`
- Zig (`.zig`, `build.zig`): `~/.claude/custom/KNOWLEDGE/zig/_rules.md`
- No matching pack: `~/.claude/custom/KNOWLEDGE/general/_rules.md`

Mode files add only mode-specific packs.

## Workflow

1. Re-read `~/.claude/custom/RESOLVER.md` only when the rules injection is not visible this
   session and the mode is not already clear.
2. Read the selected `modes/<mode>.md`; then, in one batched read, load the references it
   names and the knowledge packs selected by the table above plus the mode's additions.
3. Inspect real files, diffs or sources before making claims.
4. Separate confirmed facts from assumptions and blockers.
5. Produce findings, plan, report or spec in the mode-specific format.
6. Stop at the analysis deliverable.

## Local References

- `references/evidence-rules.md`
- `references/output-format.md`
- `references/handoff-to-implementation.md`

Mode files name additional local references.

## Output

Return or write the requested artifact. For reviews, findings come first and summaries are secondary.

For substantial work, finish with the `TRACE` block (template in the injected RESOLVER.md;
fallback: `~/.claude/custom/_core/skill-context.md`).

## Stop Conditions

- Do not edit production code or project configuration.
- Do not run implementation, deployment or release steps.
- Do not require another skill folder.
- If the user asks for code changes and no approved plan or concrete directive exists, stop with an implementation handoff.
