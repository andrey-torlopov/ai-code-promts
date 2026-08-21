# No Abstraction Layer

## Why this is bad

URLSession/URLRequest directly in tests:
- When changing the URL, you need to edit dozens of tests
- Duplication of request configuration code
- Difficult to add logging/retry/auth
- Tests know too much about the API implementation

## Bad Example

```swift
// ❌ BAD: Raw URLSession directly in each test
func testUserCanRegister() async throws {
    var request = URLRequest(url: URL(string: "https://api.example.com/api/v1/users/register")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("secret-key", forHTTPHeaderField: "X-Api-Key")
    request.httpBody = try JSONEncoder().encode(payload)

    let (data, response) = try await URLSession.shared.data(for: request)
    let httpResponse = response as! HTTPURLResponse
    XCTAssertEqual(httpResponse.statusCode, 201)
}

func testRegistrationFailsWithInvalidEmail() async throws {
    // Same boilerplate again...
    var request = URLRequest(url: URL(string: "https://api.example.com/api/v1/users/register")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("secret-key", forHTTPHeaderField: "X-Api-Key")
    request.httpBody = try JSONEncoder().encode(invalidPayload)
}
```

## Good Example

```swift
// ✅ GOOD: APIClient encapsulates HTTP
struct APIClient {
    let baseURL: URL
    let session: URLSession

    func register(_ request: RegisterRequest) async throws -> APIResponse<UserResponse> {
        try await execute(.post, path: Endpoints.register, body: request)
    }
}

// Tests are clean and readable
func testUserCanRegister() async throws {
    let response = try await apiClient.register(TestData.validRegistration())
    XCTAssertEqual(response.statusCode, 201, "Registration should succeed with valid payload")
}
```

## What to look for in code review

- `URLSession.shared.data(for:)` directly in test methods
- Duplicate URLs, headers, httpMethod
- Manual creation of `URLRequest` in each test
- Hardcode URL in tests (`"https://..."`)
- `JSONEncoder().encode()` / `JSONDecoder().decode()` ​​in each test instead of the common APIClient
