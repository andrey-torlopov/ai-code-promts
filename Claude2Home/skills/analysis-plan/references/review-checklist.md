# Review Checklist

Generic sections apply to any language. The Swift-specific section applies only when the
reviewed scope is Swift.

## Correctness

- Requirements mismatch.
- Broken state transitions.
- Missing edge cases.
- Error path returns success.
- Incorrect null/optional handling.

## Error Handling

- Swallowed errors and empty catch blocks.
- Errors converted to silent fallback values.
- Infrastructure error exposed as business error.

## Architecture

- View owns business logic.
- Presentation layer owns rendering details that belong to the view.
- Hard dependency where a boundary abstraction already exists.
- Large file, type or method that blocks comprehension.

## Security and Logging

- PII in logs, tests, mock data or design-time preview surfaces.
- Debug printing in production code.
- Sensitive data in error messages.

## Swift-Specific (Swift scope only)

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
