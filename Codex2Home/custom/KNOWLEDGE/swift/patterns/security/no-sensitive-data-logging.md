# No Sensitive Data Logging

**Applies to:** Logging, Analytics, Crash reporting

## Why this is bad

Logging sensitive data:
- Tokens and passwords go to Console.app and CI logs
- Crashlytics/Sentry reports with secrets are available to the entire team
- os_log with sensitive data is saved on the device
- Violation of compliance (GDPR, PCI DSS)
- Analytics with PII is sent to third-party servers

## Bad Example

```swift
// ❌ BAD: Token in logs
func authenticate(token: String) async throws -> AuthResponse {
    logger.info("Authenticating with token: \(token)")
    return try await apiClient.auth(token: token)
}

// ❌ BAD: Password in assertion message (tests)
XCTAssertEqual(response.statusCode, 200, "Auth failed for password=\(password)")

// ❌ BAD: Full response body with tokens
func logResponse(_ response: APIResponse<AuthResponse>) {
    print("Response: \(response.body)")
    // body contains accessToken, refreshToken
}

// ❌ BAD: UserDefaults with sensitive data are visible in device logs
UserDefaults.standard.set(apiKey, forKey: "apiKey")
logger.debug("Saved API key to UserDefaults")
```

## Good Example

```swift
// ✅ GOOD: Masked token in logs
func authenticate(token: String) async throws -> AuthResponse {
    let masked = String(token.prefix(4)) + "****"
    logger.info("Authenticating with token: \(masked)")
    return try await apiClient.auth(token: token)
}

// ✅ GOOD: os_log with privacy
import os

let logger = Logger(subsystem: "com.app", category: "auth")

func authenticate(token: String) async throws {
    logger.info("Authenticating with token: \(token, privacy: .private)")
    // In the release build, the token is replaced with <private>
}

// ✅ GOOD: Log only the structure, not the values
func logResponse<T>(_ response: APIResponse<T>) {
    logger.info("Response: status=\(response.statusCode), type=\(T.self)")
}

// ✅ GOOD: Keychain instead of UserDefaults for secrets
try KeychainHelper.save(apiKey, forKey: "apiKey")
```

## What to look for in code review

- `print()`, `NSLog()`, `logger.info()` with interpolated secrets
- `os_log` without `privacy: .private` ​​for sensitive fields
- Response body is logged entirely (may contain tokens)
- `UserDefaults` for storing tokens/passwords instead of Keychain
- Crashlytics custom keys with PII
- Analytics events with email, phone, name
- `debugPrint()` left in production code
