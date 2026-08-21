# Anti-Pattern: XCTestCase Setup Crashes

## Problem

Heavy initialization in `init()` or property declaration XCTestCase causes a crash
the entire test class without diagnostics. XCTest skips the entire class.

## Bad Example

```swift
// ❌ BAD: Property initialization may fail
class APITests: XCTestCase {
    let apiClient = APIClient(
        configuration: APIConfiguration(
            baseURL: URL(string: ProcessInfo.processInfo.environment["BASE_URL"]!)!
        )
    )
    // If BASE_URL is not set - force unwrap in init, the entire class is skipped

    func testCreateUser() async throws { /* ... */ }
}

// ❌ BAD: Complex logic in init
class DatabaseTests: XCTestCase {
    let database: Database

    override init() {
        database = try! Database.connect(to: "test.db") // May crash
        super.init()
    }
}
```

## Good Example

```swift
// ✅ GOOD: Initialization in setUp
class APITests: XCTestCase {
    var apiClient: APIClient!

    override func setUp() async throws {
        try await super.setUp()

        let baseURLString = ProcessInfo.processInfo.environment["BASE_URL"] ?? "http://localhost:8080"
        guard let baseURL = URL(string: baseURLString) else {
            XCTFail("Invalid BASE_URL: \(baseURLString)")
            return
        }

        apiClient = APIClient(
            configuration: APIConfiguration(baseURL: baseURL)
        )
    }

    override func tearDown() async throws {
        apiClient = nil
        try await super.tearDown()
    }

    func testCreateUser() async throws { /* ... */ }
}
```

## Why

- `setUp()` runs after successful class initialization
- Setup errors are isolated from the class and provide clear diagnostics
- Cleanup guaranteed via `tearDown()`
- Force unwrap in property declaration crashes without a clear message

## Detection

```bash
# Property init with force unwrap in tests
grep -rn "let .* = .*!" --include="*Tests.swift" Tests/ | grep -v "IBOutlet\|XCTUnwrap"
# Force try in test classes (not in test methods)
grep -rn "try!" --include="*Tests.swift" Tests/
```

## References

- (ref: platform/xctest-setup-crashes.md)
- Apple: XCTestCase lifecycle
