# Diagnosis Core

Log analysis and root-cause reporting in one file; loaded for every diagnosis mode.

## Log Analysis

1. Capture the exact failing command or job name when available.
2. Identify the first meaningful error, not only the final summary.
3. Separate primary failure from cascading failures.
4. Classify a crash artifact before interpreting it; on Apple platforms start from
   `~/.claude/custom/KNOWLEDGE/swift/debugging/crash-triage.md`.
5. Decode every hex constant from the field it appeared in, using
   `~/.claude/custom/KNOWLEDGE/swift/debugging/hex-codes.md`.
6. Link each hypothesis to a log line, file or command result.
7. State missing evidence explicitly, including symbolication status and build configuration.

Anti-patterns:

- Treating warnings as root cause without evidence.
- Ignoring the first failure in favor of a familiar later error.
- Recommending broad cleanup before identifying a cause.
- Guessing the meaning of a hex code, or reporting the code itself as the root cause.
- Reading a termination code as a memory address, or a fault address as a termination code.

## Root Cause Format

Use this structure:

```text
Symptom:
Evidence:
Root cause:
Fix plan:
Verification:
Residual risk:
```

If root cause is not proven, say `Most likely cause` and list the missing evidence.
