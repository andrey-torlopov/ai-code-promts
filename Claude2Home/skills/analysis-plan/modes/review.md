# Mode: review

Use for read-only code, diff or PR review.

## Knowledge

Load by scope:

- Swift: `~/.claude/custom/KNOWLEDGE/swift/_rules.md`
- Swift patterns on signal: `~/.claude/custom/KNOWLEDGE/swift/patterns/<category>/`
- CI or deploy config review: `~/.claude/custom/KNOWLEDGE/devops/_rules.md`
- Shell scripts: `~/.claude/custom/KNOWLEDGE/shell/_rules.md`
- Python: `~/.claude/custom/KNOWLEDGE/python/_rules.md`
- No matching domain pack: `~/.claude/custom/KNOWLEDGE/general/_rules.md`

## References

- `../references/review-checklist.md`
- `../references/review-severity-model.md`
- `../references/diff-review-mode.md`
- `../references/critical-only-review-mode.md`
- `../references/swift-concurrency-review-rules.md`
- `../references/swift-pattern-loading.md`

## Workflow

1. Inspect real files or diff before writing findings.
2. Load pattern categories only after a concrete signal appears.
3. Report findings first, ordered by severity.
4. Include file and line when available.
5. For each finding, explain impact, specific fix and verification or test gap.

## Stop

Do not modify code. If there are no findings, state that clearly and mention residual risk from unrun checks.
