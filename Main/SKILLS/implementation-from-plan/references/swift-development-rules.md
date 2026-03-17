# Swift Development Rules

- Prefer `let` over `var` unless mutation is required.
- Prefer value types when reference identity is not needed.
- Mark classes `final` unless inheritance is intended.
- Avoid force unwraps and `try!` outside narrow, justified test setup.
- Avoid empty `catch`.
- Prefer `@MainActor` for UI state over manual `DispatchQueue.main`.
- Avoid `Thread.sleep` and arbitrary `Task.sleep` in tests; use deterministic polling or expectations.
- Do not replace typed models with `[String: Any]`.
- Do not log sensitive data.
- For escaping closures, inspect retain cycles and use capture lists when needed.
