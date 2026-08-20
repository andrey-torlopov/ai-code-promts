# Swift Review Checklist

## Correctness

- Requirements mismatch.
- Broken state transitions.
- Missing edge cases.
- Error path returns success.
- Incorrect optional handling.

## Memory Safety

- Escaping closure captures `self` strongly.
- Delegate or data source is not `weak`.
- Timer or notification callback keeps owner alive.
- `unowned` without proof of lifetime.
- Force unwrap or implicitly unwrapped optional without narrow justification.

## Error Handling

- Empty `catch`.
- `try?` loses meaningful failure.
- `fatalError` in production path.
- Infrastructure error exposed as business error.

## Swift Style With Risk

- `var` where mutation is not needed.
- Reference type where value semantics are expected.
- Untyped dictionaries replacing models.
- Naming that hides behavior or side effects.

## Architecture

- View owns business logic.
- ViewModel owns UI rendering details.
- Hard dependency where protocol boundary already exists.
- Large file, type or method that blocks comprehension.

## Security and Logging

- PII in logs, previews, tests or mock data.
- `print` in production code.
- Sensitive data in error messages.
