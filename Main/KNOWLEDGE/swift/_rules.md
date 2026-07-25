# Swift Rules

1. Prefer the project's existing architecture and conventions.
2. Inspect `Package.swift`, Xcode projects and source layout before choosing commands.
3. Prefer value types and `let` unless mutation or reference semantics are required.
4. Keep concurrency explicit: actors, `Sendable`, `@MainActor` and shared state need evidence.
5. Avoid infrastructure calls hidden inline in business logic when the project already has an abstraction.
6. Do not log sensitive data.
7. Avoid flaky tests based on sleep; prefer deterministic waits.
8. Use typed models for stable API data instead of `[String: Any]`.
9. Verification should be focused and named explicitly.
10. Load pattern categories only when concrete signals appear.
11. When a crash report or log contains a hex constant, decode it from `debugging/hex-codes.md`; never guess the meaning of a code.
12. Treat a decoded termination code as the kill reason, not the root cause; the root cause stays in the backtrace.
