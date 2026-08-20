# Mode: refactor

Use for prioritized refactoring plans with risk, dependencies and execution order.

## Knowledge

Load by scope:

- Swift: `~/.claude/custom/KNOWLEDGE/swift/_rules.md`
- Swift patterns only when signals are present: `~/.claude/custom/KNOWLEDGE/swift/patterns/<category>/`
- iOS architecture: `~/.claude/custom/KNOWLEDGE/ios/architecture-feature-first.md`

## References

- `../references/refactor-smell-catalog.md`
- `../references/refactor-risk-model.md`
- `../references/refactor-report-format.md`
- `../references/evidence-rules.md`

## Workflow

1. Verify scope exists and enumerate files.
2. Read the files or explicitly state exclusions.
3. Count all relevant files, lines, types and obvious dependencies.
4. Detect structural, design and domain-specific smells from evidence.
5. Build a dependency-aware sequence with risk and verification per phase.

## Stop

Write or return the refactor plan. Do not implement.
