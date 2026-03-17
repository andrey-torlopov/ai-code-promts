# No Cleanup Pattern

## Why this is bad

Tests without data cleaning:
- Clog the database/UserDefaults/Keychain with test records
- Create flaky tests (uniqueness conflicts)
- Make parallel running impossible
- Makes debugging more difficult in staging/dev environments

## Bad Example

```swift
// ❌ BAD: Data remains forever
func testUserCanRegister() async throws {
    let payload = RegisterRequest(
        email: "test_\(Int(Date().timeIntervalSince1970))@example.com"
    )

    let response = try await apiClient.register(payload)
    XCTAssertEqual(response.statusCode, 201, "Registration should succeed")
    // The test is over, the user remains in the database
}
```

## Good Example

```swift
// ✅ GOOD: defer guarantees cleanup
func testUserCanRegister() async throws {
    let response = try await apiClient.register(validPayload)
    XCTAssertEqual(response.statusCode, 201, "Registration should succeed")

    let userId = response.body.userId

    // addTeardownBlock will be executed even if the test fails
    addTeardownBlock { [weak self] in
        try? await self?.apiClient.deleteUser(userId)
    }
}

// ✅ GOOD: setUp cleanup before each test
override func setUp() async throws {
    try await super.setUp()
    try? await apiClient.deleteUserByEmail(testEmail)
}

func testUserCanRegister() async throws {
    let response = try await apiClient.register(payload)
    XCTAssertEqual(response.statusCode, 201, "Registration should succeed")
}
```

## Recommended strategy: Cleanup-First

**Cleanup in `setUp()` (not `tearDown()`)** is the recommended approach for integration tests.

**Why Cleanup-First is better than Cleanup-After:**
- When a test fails, the data is saved for debugging
- The next launch will clean up in front of itself (idempotently)
- `tearDown()` may not be executed if the process crashes

| Strategy | When |
|-----------|-------|
| **Cleanup-First (`setUp`)** | Integration tests, shared DB, crash debugging needed |
| **`addTeardownBlock`** | The test creates a unique resource that needs to be deleted immediately |
| **Cleanup-After (`tearDown`)** | Only if Cleanup-First is not possible |

## What to look for in code review

- Missing `addTeardownBlock`, `setUp` ​​cleanup or `tearDown`
- "Unique prefixes" as the only isolation strategy
- Tests that crash when run again
- `tearDown` instead of `setUp` ​​cleanup without justification
- Cleanup operations that are not idempotent (fail if the resource does not exist)
