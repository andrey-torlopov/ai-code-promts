# Swift Verification

Prefer focused verification:

1. If `Package.swift` exists, consider `swift build` and `swift test`.
2. If an Xcode project exists, inspect schemes before using `xcodebuild`.
3. For changed tests, run the narrowest relevant test target first.
4. For dependency changes, inspect lockfiles and resolved versions.
5. If verification is not run, report the exact blocker.
