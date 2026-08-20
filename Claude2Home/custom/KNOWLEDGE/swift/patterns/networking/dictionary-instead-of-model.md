# Dictionary Instead of Codable Model

## Why this is bad

Using `[String: Any]` instead of typed Codable models:
- The compiler does not catch typos in field names
- No autocompletion in IDE
- When refactoring an API, you need to search for strings throughout the project
- It is impossible to understand the data structure without documentation
- Type safety is lost - one of the main advantages of Swift

## Bad Example

```swift
// ❌ BAD: Dictionary - the compiler will not help
func register() async throws {
    let payload: [String: Any] = [
        "email": "test@example.com",
        "phone": "+79991234567",
        "password": "Test123!", // Typo! The compiler is silent
        "full_name": "Test User"
    ]

    let data = try JSONSerialization.data(withJSONObject: payload)
    var request = URLRequest(url: registerURL)
    request.httpBody = data
    // ...
}
```

## Good Example

```swift
// ✅ GOOD: Codable struct with CodingKeys
struct RegisterRequest: Codable, Sendable {
    let email: String
    let phone: String
    let password: String // Typo = compilation error
    let fullName: String

    enum CodingKeys: String, CodingKey {
        case email, phone, password
        case fullName = "full_name"
    }
}

func register() async throws {
    let payload = RegisterRequest(
        email: "test@example.com",
        phone: "+79991234567",
        password: "Test123!", // IDE prompts
        fullName: "Test User"
    )

    let response = try await apiClient.register(payload)
}
```

## What to look for in code review

- `[String: Any]`, `[String: String]` ​​for request/response body
- `JSONSerialization.data(withJSONObject:)` instead of `JSONEncoder().encode()`
- JSON strings collected via string interpolation
- Lack of Codable models in the `Models/` or `DTOs/` ​​folder
- Type casting via `as? String`, `as? Int` ​​when parsing a response
