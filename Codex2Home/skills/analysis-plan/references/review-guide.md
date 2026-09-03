# Review Guide

Checklist, severity model, diff procedure and critical-only mode in one file.
Generic sections apply to any language; the Swift-specific section applies only when the
reviewed scope is Swift.

## Checklist

### Correctness

- Requirements mismatch.
- Broken state transitions.
- Missing edge cases.
- Error path returns success.
- Incorrect null/optional handling.

### Error Handling

- Swallowed errors and empty catch blocks.
- Errors converted to silent fallback values.
- Infrastructure error exposed as business error.

### Architecture

- View owns business logic.
- Presentation layer owns rendering details that belong to the view.
- Hard dependency where a boundary abstraction already exists.
- Large file, type or method that blocks comprehension.

### Security and Logging

- PII in logs, tests, mock data or design-time preview surfaces.
- Debug printing in production code.
- Sensitive data in error messages.

### Swift-Specific (Swift scope only)

Memory safety:

- Escaping closure captures `self` strongly.
- Delegate or data source is not `weak`.
- Timer or notification callback keeps owner alive.
- `unowned` without proof of lifetime.
- Force unwrap or implicitly unwrapped optional without narrow justification.

Style with risk:

- `var` where mutation is not needed.
- Reference type where value semantics are expected.
- Untyped dictionaries replacing models.
- `try?` loses meaningful failure.
- `fatalError` in production path.
- Naming that hides behavior or side effects.

## Severity Model

| Severity | Meaning |
|---|---|
| `BLOCKER` | Likely crash, data loss, security leak, severe data race or change that must not ship |
| `CRITICAL` | Real bug or high-risk behavior with clear reproduction path |
| `WARNING` | Maintainability or correctness risk that should be fixed soon |
| `INFO` | Low-risk observation or test gap |

Rules:

- Findings must be actionable.
- Do not report taste-only comments.
- If evidence is weak, mark it as an assumption or omit it.
- Put findings before summary.

## Diff Review (when reviewing a diff or PR)

1. Inspect changed file list.
2. Inspect unstaged and staged diffs if reviewing local git state.
3. Read complete modified files when needed for context.
4. Review only behavior touched by the diff unless a nearby issue directly affects the change.

Output:

```text
Findings:
Summary:
Verification / Test Gaps:
```

Do not rewrite the diff during review.

## Critical-Only Mode (when the user asks for critical-only findings)

Report only: crashes, data loss, security leaks, data races, severe memory leaks or retain
cycles, incorrect behavior that blocks release.

Do not include: style nits, minor naming, optional refactors, low-confidence observations.

If no critical issues are found, say so directly.
