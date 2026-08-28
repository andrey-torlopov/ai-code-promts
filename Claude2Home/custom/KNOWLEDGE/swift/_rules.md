# Swift Rules

1. Prefer the project's existing architecture and conventions.
2. Inspect `Package.swift`, Xcode projects and source layout before choosing commands.
3. Prefer value types and `let` unless mutation or reference semantics are required.
4. Keep concurrency explicit: actors, `Sendable`, `@MainActor` and shared state need evidence.
5. Avoid infrastructure calls hidden inline in business logic when the project already has an abstraction.
6. Do not log sensitive data; in production logs avoid `String(describing: error)` and `\(error)` — they leak internals.
7. Avoid flaky tests based on sleep; prefer deterministic waits.
8. Use typed models for stable API data instead of `[String: Any]`.
9. Avoid `String(describing:)`, `"\(T.self)"` and `"\(type(of: x))"` in hot paths, at startup and as cache or registry keys; prefer `_typeName`, `ObjectIdentifier` or `CustomStringConvertible` (details: `patterns/performance/string-describing-reflection.md`).
10. Verification should be focused and named explicitly.
11. Load pattern categories only when concrete signals appear (entry: `patterns/_summary-index.md`).
12. For any crash, hang or stackshot artifact, classify with `debugging/crash-triage.md` before decoding constants or reading a backtrace.
13. Decode hex constants from `debugging/hex-codes.md` using the field they came from; never guess a code and never quote a community-only code as documented.
14. Treat a decoded termination code as the kill reason, not the root cause; the root cause stays in the backtrace of the blocked or faulting thread.
15. Do not quote an unsymbolicated backtrace as evidence; state symbolication status first.
16. When backtraces differ across otherwise identical crashes, escalate to `debugging/memory-diagnostics.md` instead of reading individual stacks.
