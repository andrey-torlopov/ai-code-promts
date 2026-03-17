# Anti-Pattern: URLSession is created inline in the code

## Problem

`URLSession` or `URLRequest` ​​are created directly at the point of use.
Each call manages its own session - there is no single point of configuration.

## Bad Example

```swift
// ❌ BAD: inline URLSession in each method
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/api/v1/users/\(id)")!
    var request = URLRequest(url: url)
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

    let (data, response) = try await URLSession.shared.data(for: request)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw APIError.invalidResponse
    }
    return try JSONDecoder().decode(User.self, from: data)
}
```

## Good Example

```swift
// ✅ GOOD: Requests via APIClient with a single configuration
func fetchUser(id: String) async throws -> User {
    try await apiClient.request(
        .get,
        path: "/users/\(id)",
        responseType: User.self
    )
}
```

## Why

- Inline session does not reuse the connection pool - slow requests
- No single point for Logging, Auth, Retry configuration
- When changing baseURL you need to update N places, not just one Config
- It is impossible to replace the session for tests (mock/stub)

## Detection

```bash
grep -rn "URLSession.shared\|URLSession(" --include="*.swift" Sources/
```

## References

- (ref: networking/inline-urlsession-calls.md)
- General principle: `common/no-abstraction-layer.md`
