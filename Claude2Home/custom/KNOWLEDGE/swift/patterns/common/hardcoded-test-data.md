# Hardcoded Test Data

**Applies to:** Unit tests, UI tests, snapshot tests

## Why this is bad

Hardcoded data in tests:
- Hides the logic for selecting test data (why this particular value?)
- When requirements change, you need to look for all places with hardcode
- It is impossible to reuse the test for other environments
- Tester copies values ​​instead of understanding boundary conditions

## Bad Example

```swift
// ❌ BAD: Specific values ​​without explanation
func testSuccessfulRegistration() async throws {
    let request = RegisterRequest(
        email: "test@example.com", // Why this one?
        password: "Password123!", // Specific password is hardcoded
        fullName: "Test User"
    )

    let response = try await apiClient.register(request)
    XCTAssertEqual(response.statusCode, 201)
}
```

## Good Example

```swift
// ✅ GOOD: Factory with a description of the data class
enum TestData {
    static func validRegistration() -> RegisterRequest {
        RegisterRequest(
            email: "auto_\(Int(Date().timeIntervalSince1970))@example.com",
            password: "Test#\(UUID().uuidString.prefix(8))",
            fullName: "Test User"
        )
    }
}

// ✅ GOOD: For BVA - specify the boundary, not a specific value
func testMinimumPasswordLength() async throws {
    // Minimum limit: exactly 8 characters
    let request = TestData.validRegistration()
        .with(password: String(repeating: "A", count: 8) + "1!")

    let response = try await apiClient.register(request)
    XCTAssertEqual(response.statusCode, 201, "Password at minimum boundary should be accepted")
}
```

## What to look for in review

- Specific email/phone/password directly in the body of the test
- Lack of explanation "why this value" (boundary? valid? invalid?)
- Same literal values ​​in different tests
- Lack of TestData factory/fixture builder
