---
name: implementation-from-plan
description: Implements an approved plan or direct concrete edit request, then verifies and reports changed files, checks and residual risk. Use for code, config or instruction changes after the deliverable boundary permits edits.
---

# Implementation From Plan

Skill root: `$CODEX_HOME/skills/implementation-from-plan/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

This skill changes files only when implementation is explicitly requested.

## SKILL CONTEXT

Before substantial work, output the block from `$CODEX_HOME/custom/_core/skill-context.md`.

For domain work, show loaded knowledge packs. For example:

- Swift: `$CODEX_HOME/custom/KNOWLEDGE/swift/_rules.md`
- Swift patterns on signal: `$CODEX_HOME/custom/KNOWLEDGE/swift/patterns/<category>/` (entry: `patterns/_summary-index.md`)
- iOS: `$CODEX_HOME/custom/KNOWLEDGE/ios/_rules.md`
- DevOps: `$CODEX_HOME/custom/KNOWLEDGE/devops/_rules.md`
- Shell: `$CODEX_HOME/custom/KNOWLEDGE/shell/_rules.md`
- Python: `$CODEX_HOME/custom/KNOWLEDGE/python/_rules.md`
- Other stacks, no matching pack: `$CODEX_HOME/custom/KNOWLEDGE/general/_rules.md`

## Inputs

- Approved plan path or direct concrete implementation request.
- Scope and allowed files.
- Acceptance criteria.
- Verification expectations.

## Workflow

1. Read the plan or concrete directive.
2. Read `references/delivery-pipeline.md`.
3. Read domain references only when the scope requires them.
4. Inspect real files before editing.
5. When writing or editing Swift code, load the matching `$CODEX_HOME/custom/KNOWLEDGE/swift/patterns/<category>/` pattern file after a concrete signal; never preload all categories.
6. Make the smallest change that satisfies the accepted scope.
7. Add or update tests only when requested, required by the plan or necessary for risky behavior.
8. Run focused verification where available.
9. Review the diff against the request and acceptance criteria.
10. Report changed files, verification and residual risk.

## Local References

- `references/delivery-pipeline.md`
- `references/swift-development-rules.md`
- `references/swift-verification-rules.md`
- `references/self-review.md`
- `references/change-report.md`

## Output

Return:

1. Changed files.
2. Verification commands and results.
3. Residual risk.
4. Final `TRACE`.

## Stop Conditions

- Do not start if the request is only analysis, planning or review.
- Do not expand architecture beyond the approved plan or concrete directive.
- Do not deploy, release, publish or roll out.
- Do not require another skill folder.
