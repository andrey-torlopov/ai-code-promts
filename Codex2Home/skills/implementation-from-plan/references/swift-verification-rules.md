# Verification Rules

SwiftPM:

```text
swift build
swift test
```

Xcode:

- Inspect available projects and schemes before constructing `xcodebuild`.
- Prefer the narrowest scheme and destination that validates the change.

If verification cannot run:

- State the command that would be run.
- State the exact blocker.
- State residual risk.

Do not claim verification passed without command output or a clear deterministic check.
