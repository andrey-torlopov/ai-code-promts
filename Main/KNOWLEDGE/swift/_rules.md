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
11. For any crash, hang or stackshot artifact, classify with `debugging/crash-triage.md` before decoding constants or reading a backtrace.
12. Decode hex constants from `debugging/hex-codes.md` using the field they came from; never guess a code and never quote a community-only code as documented.
13. Treat a decoded termination code as the kill reason, not the root cause; the root cause stays in the backtrace of the blocked or faulting thread.
14. Do not quote an unsymbolicated backtrace as evidence; state symbolication status first.
15. When backtraces differ across otherwise identical crashes, escalate to `debugging/memory-diagnostics.md` instead of reading individual stacks.
