# Anti-Pattern: No Security Headers check

## Problem

The Networking layer does not check the security headers of the response.
The server returns 200, but there are no security headers - the vulnerability goes undetected.

## Bad Example

```swift
// ❌ BAD: No security headers check in the API client
func fetchUser(id: String) async throws -> User {
    let (data, response) = try await session.data(for: request)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw APIError.invalidResponse
    }

    return try decoder.decode(User.self, from: data)
    // X-Content-Type-Options, HSTS - not checked
}
```

## Good Example

```swift
// ✅ GOOD: Checking security headers in API tests
func testRegistrationResponseHeaders() async throws {
    let response = try await apiClient.register(TestData.validRegistration())
    XCTAssertEqual(response.statusCode, 201, "Registration should succeed")

    let headers = response.allHeaderFields
    XCTAssertEqual(
        headers["X-Content-Type-Options"] as? String,
        "nosniff",
        "X-Content-Type-Options header should be nosniff"
    )
    XCTAssertNotNil(
        headers["Strict-Transport-Security"],
        "HSTS header must be present"
    )
}

// ✅ GOOD: Logging suspicious responses without HSTS in production
func validateSecurityHeaders(_ response: HTTPURLResponse) {
    #if DEBUG
    let requiredHeaders = ["X-Content-Type-Options", "Strict-Transport-Security"]
    for header in requiredHeaders {
        if response.value(forHTTPHeaderField: header) == nil {
            assertionFailure("Missing security header: \(header)")
        }
    }
    #endif
}
```

## Checklist (Security Headers)

| Header | Expected value |
|--------|----------------|
| `Content-Type` | `application/json` ​​(or according to spec) |
| `X-Content-Type-Options` | `nosniff` |
| `Strict-Transport-Security` | present (`max-age=...`) |

## What to look for in code review

- No test checks security headers
- Lack of debug validation of headers in the networking layer
- ATS (App Transport Security) is disabled without justification in Info.plist
- `NSAllowsArbitraryLoads = true` in production
