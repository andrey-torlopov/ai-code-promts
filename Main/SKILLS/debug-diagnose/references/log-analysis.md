# Log Analysis

## Workflow

1. Capture the exact failing command or job name when available.
2. Identify the first meaningful error, not only the final summary.
3. Separate primary failure from cascading failures.
4. Link each hypothesis to a log line, file or command result.
5. State missing evidence explicitly.

## Anti-Patterns

- Treating warnings as root cause without evidence.
- Ignoring the first failure in favor of a familiar later error.
- Recommending broad cleanup before identifying a cause.
