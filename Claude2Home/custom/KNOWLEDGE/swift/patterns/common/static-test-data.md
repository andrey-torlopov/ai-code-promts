# Static Test Data

**Applies to:** Unit tests, Integration tests

## Why this is bad

Static data in TestData/Factory:
- Conflicts when running in parallel (same email/phone)
- Cannot run test twice without cleanup
- Flaky tests due to `UNIQUE constraint violation`
- Hide isolation problems between tests

## Bad Example

```swift
// ❌ BAD: Static constants
enum RegistrationTestData {
    static let validEmail = "test@example.com" // Conflict on second launch
    static let validPhone = "+79991234567"
    static let validPassword = "Password123!"

    static func validRequest() -> RegisterRequest {
        RegisterRequest(
            email: validEmail, // Always the same
            phone: validPhone,
            password: validPassword
        )
    }
}

// ❌ BAD: Hardcode without generation
static func validRequest() -> RegisterRequest {
    RegisterRequest(
        email: "fixed_test@example.com", // Statics!
        phone: "+70001112233",
        password: "Test123!"
    )
}
```

## Good Example

```swift
// ✅ GOOD: Factory with unique data generation
enum RegistrationTestData {

    static func validRequest() -> RegisterRequest {
        let suffix = Int(Date().timeIntervalSince1970)
        return RegisterRequest(
            email: "auto_\(suffix)@example.com",
            phone: "+7\(Int.random(in: 9_000_000_000...9_999_999_999))",
            password: "Test#\(UUID().uuidString.prefix(8))",
            fullName: "Test User"
        )
    }

    // Modifications via copy-pattern
    static func withInvalidEmail() -> RegisterRequest {
        var request = validRequest()
        request.email = "invalid-email-no-at-sign"
        return request
    }

    static func withWeakPassword() -> RegisterRequest {
        var request = validRequest()
        request.password = "weak"
        return request
    }
}
```

## Pattern: Unique Suffix Generator

```swift
// ✅ Reusable generator
enum TestDataUtils {
    static func uniqueSuffix() -> String {
        "\(Int(Date().timeIntervalSince1970))_\(Int.random(in: 1000...9999))"
    }

    static func uniqueEmail(prefix: String = "auto") -> String {
        "\(prefix)_\(uniqueSuffix())@example.com"
    }

    static func uniquePhone() -> String {
        "+7\(Int.random(in: 9_000_000_000...9_999_999_999))"
    }
}
```

## What to look for in code review

- `static let` with fixed email/phone/id in test data
- Factory functions without `Date()` or `UUID()` ​​for unique fields
- No randomization in data that should be unique
- Tests with `skip` / comments about "data conflicts"
