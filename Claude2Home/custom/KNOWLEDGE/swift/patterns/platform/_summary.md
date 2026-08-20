# Platform Patterns

- Prefer async XCTest methods over legacy expectation chains when available.
- Avoid `Thread.sleep` and arbitrary `Task.sleep` for waiting in tests.
- Avoid force unwraps and `try!` in XCTest property initialization.
- Protect shared mutable state with actors, isolation or a justified synchronization primitive.
- Keep retry policies bounded and observable.
- Avoid magic timeout constants; name and centralize them.
