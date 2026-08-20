# Swift Conventions

Use local project style first.

Fallback conventions:

- `final class` when inheritance is not intended.
- `struct` for simple value data.
- `let` by default.
- Descriptive XCTest failure messages for non-obvious assertions.
- Explicit dependency injection for networking, clocks, UUIDs and file systems when testability matters.
- Avoid broad refactors during focused fixes.
