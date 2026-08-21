# Swift Best Practices

- Prefer `let` by default; use `var` only when mutation is required.
- Prefer `struct` and value semantics unless identity, inheritance or shared mutable state is necessary.
- Mark classes `final` unless subclassing is part of the design.
- Prefer `guard` for early exits when it reduces nesting.
- Keep optional handling explicit; avoid hiding errors in optional chains when failure matters.
