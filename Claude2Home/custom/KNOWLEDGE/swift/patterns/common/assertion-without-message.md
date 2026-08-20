# Assertion Without Message

## Why this is bad

XCTest assertions without messages:
- When falling, it is not clear what exactly was checked
- CI logs contain only stack trace without context
- You need to open the code to understand the reason
- Xcode Test Reports become useless

## Bad Example

```swift
// ❌ BAD: What fell? Why?
func testUserRegistration() async throws {
    let response = try await apiClient.register(payload)

    XCTAssertEqual(response.statusCode, 201)        // XCTAssertEqual failed: ("400") is not equal to ("201")
    XCTAssertNotNil(response.body.userId) // Which userId? Why nil?
    XCTAssertEqual(response.body.status, "pending")
}

// In CI logs:
// XCTAssertEqual failed: ("400") is not equal to ("201")
//What went wrong?
```

## Good Example

```swift
// ✅ GOOD: XCTAssert with message
func testUserRegistration() async throws {
    let response = try await apiClient.register(payload)

    XCTAssertEqual(response.statusCode, 201, "Registration should return 201 for valid payload")
    XCTAssertNotNil(response.body.userId, "User ID should be returned after successful registration")
    XCTAssertEqual(response.body.status, "pending", "New user should have pending status until verification")
}

// ✅ GOOD: XCTContext.runActivity for grouping checks
func testUserRegistration() async throws {
    let response = try await apiClient.register(payload)

    XCTContext.runActivity(named: "Verify HTTP 201 Created") { _ in
        XCTAssertEqual(response.statusCode, 201, "Registration should succeed")
    }

    XCTContext.runActivity(named: "Verify user ID is returned") { _ in
        XCTAssertNotNil(response.body.userId, "User ID should be present")
    }
}
```

## What to look for in code review

- `XCTAssertEqual`, `XCTAssertNotNil`, `XCTAssertTrue` without message parameter
- Several assertions in a row without context
- Lack of `XCTContext.runActivity` in integration tests
- Assertions on nested fields without explaining the structure
