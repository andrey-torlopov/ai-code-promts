# Mode: review

Use for read-only code, diff or PR review.

## Knowledge

Per the scope table in `../SKILL.md`; no mode-specific additions.

## References

- `../references/review-guide.md` - checklist, severity model, diff and critical-only procedures
- Swift scope only: `../references/swift-concurrency-review-rules.md`, `../references/swift-pattern-loading.md`

## Workflow

1. Inspect real files or diff before writing findings.
2. Load pattern categories only after a concrete signal appears.
3. Report findings first, ordered by severity.
4. Include file and line when available.
5. For each finding, explain impact, specific fix and verification or test gap.

## Stop

Do not modify code. If there are no findings, state that clearly and mention residual risk from unrun checks.
