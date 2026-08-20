# Swift Concurrency Rules

## Structured Concurrency

Prefer:

- `async let` for small parallel work.
- `withTaskGroup` for dynamic parallel work.
- `await` sequence for ordered work.
- Actor or isolated state for shared mutable state.

Be suspicious of:

- Unstructured `Task` used where a structured parent exists.
- `Task.detached` without a clear reason.
- Fire-and-forget work that affects user-visible state.

## Main Actor

- UI state and UI-facing observable models should be `@MainActor`.
- Prefer `@MainActor` or `await MainActor.run` over scattered `DispatchQueue.main.async`.

## Sendable

Check values crossing actor boundaries or used in `@Sendable` closures. `@unchecked Sendable` needs a concrete justification comment.

## Tests

Avoid arbitrary sleeps. Use expectations, deterministic polling, injected clocks or async test support.
