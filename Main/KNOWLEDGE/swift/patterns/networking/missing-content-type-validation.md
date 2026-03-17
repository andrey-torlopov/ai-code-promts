# Missing Content-Type Validation

**Applies to:** Networking layer

## Why this is bad

The code does not check the Content-Type of the response:
- The server may return HTML instead of JSON (reverse proxy error, CloudFlare challenge)
- `JSONDecoder` will throw `DecodingError` ​​instead of an understandable error
- The bug is detected only in production during integration
- Incomprehensible crash logs instead of the clear “the server did not return JSON”

## Bad Example

```swift
// ❌ BAD: We check only the status code, Content-Type is ignored
func fetchUser(id: String) async throws -> User {
    let (data, response) = try await session.data(for: request)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw APIError.invalidResponse
    }

    return try decoder.decode(User.self, from: data)
    // If the server returned HTML (502 from nginx) - we get a DecodingError
}
```

## Good Example

```swift
// ✅ GOOD: Check Content-Type before decoding
func fetchUser(id: String) async throws -> User {
    let (data, response) = try await session.data(for: request)
    guard let httpResponse = response as? HTTPURLResponse else {
        throw APIError.invalidResponse
    }

    guard httpResponse.statusCode == 200 else {
        throw APIError.serverError(statusCode: httpResponse.statusCode)
    }

    let contentType = httpResponse.value(forHTTPHeaderField: "Content-Type") ?? ""
    guard contentType.contains("application/json") else {
        throw APIError.unexpectedContentType(
            expected: "application/json",
            received: contentType,
            statusCode: httpResponse.statusCode
        )
    }

    return try decoder.decode(User.self, from: data)
}

// ✅ GOOD: Centralized validation in the base method
func request<T: Decodable>(
    _ method: HTTPMethod,
    path: String,
    responseType: T.Type
) async throws -> T {
    let (data, response) = try await session.data(for: buildRequest(method, path: path))
    try validateResponse(response, data: data)
    return try decoder.decode(T.self, from: data)
}

private func validateResponse(_ response: URLResponse, data: Data) throws {
    guard let httpResponse = response as? HTTPURLResponse else {
        throw APIError.invalidResponse
    }

    let contentType = httpResponse.value(forHTTPHeaderField: "Content-Type") ?? ""
    guard contentType.contains("application/json") else {
        throw APIError.unexpectedContentType(
            expected: "application/json",
            received: contentType,
            statusCode: httpResponse.statusCode
        )
    }
}
```

## What to look for in code review

- `JSONDecoder().decode()` without preliminary Content-Type check
- Lack of Content-Type check in the base networking layer
- Error responses (4xx/5xx) are not checked for Content-Type before parsing
- `DecodingError` in crash logs (may be a consequence of HTML instead of JSON)
