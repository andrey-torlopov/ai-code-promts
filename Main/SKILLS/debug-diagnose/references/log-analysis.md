# Log Analysis

## Workflow

1. Capture the exact failing command or job name when available.
2. Identify the first meaningful error, not only the final summary.
3. Separate primary failure from cascading failures.
4. Decode every hex constant from its own field before reasoning about it; for Apple
   platforms use `KNOWLEDGE/swift/debugging/hex-codes.md`.
5. Link each hypothesis to a log line, file or command result.
6. State missing evidence explicitly.

## Anti-Patterns

- Treating warnings as root cause without evidence.
- Ignoring the first failure in favor of a familiar later error.
- Recommending broad cleanup before identifying a cause.
- Guessing the meaning of a hex code, or reporting the code itself as the root cause.
- Reading a termination code as a memory address, or a fault address as a termination code.
