# Swift Verification

Prefer focused verification:

1. If `Package.swift` exists, consider `swift build` and `swift test`.
2. If an Xcode project exists, inspect schemes before using `xcodebuild`; prefer the
   narrowest scheme and destination that validates the change.
3. For changed tests, run the narrowest relevant test target first.
4. For dependency changes, inspect lockfiles and resolved versions.
5. If verification is not run, report the exact blocker and the residual risk.
6. Running `swift build`, `swift test` or `xcodebuild` is gated by CORE rule 9: it needs
   the user's explicit request or a `PROJECT.md` build policy; otherwise name the command
   and report the blocker.
7. Do not claim verification passed without command output or a clear deterministic check.
