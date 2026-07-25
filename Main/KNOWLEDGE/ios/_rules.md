# iOS Rules

1. Detect app structure before making architecture claims.
2. Preserve existing navigation, state management and dependency injection patterns.
3. For UIKit/SwiftUI migration, plan boundaries and interop points explicitly.
4. Treat entitlements, signing, capabilities and deployment targets as high-risk.
5. Do not invent schemes, bundle identifiers or CI commands.
6. For crash, hang or stackshot artifacts use `KNOWLEDGE/swift/debugging/`; classify with `crash-triage.md` before naming a cause.
7. Treat a system kill (watchdog, jetsam, thermal, `0xdead10cc`) as a lifecycle or resource defect in the app, not as an OS defect, until the report proves otherwise.
