# Wrap Infrastructure Errors

**Applies to:** Networking layer

## Why this is bad

Infrastructure errors (network, timeout, DNS) are indistinguishable from business errors:
- `URLError` looks like an application bug in the crash logs
- UI shows generic error instead of "No connection"
- It is impossible to distinguish between "the server returned an error" and "the network is unavailable"
- Analytics considers network timeout as app error

## Bad Example

```swift
// ❌ BAD: Infrastructure error is indistinguishable from a business error
func createUser(_ request: CreateUserRequest) async throws -> UserResponse {
    let (data, response) = try await session.data(for: buildRequest(request))
    // URLError.timedOut, URLError.notConnectedToInternet are thrown as is
    // Calling code does not distinguish between reasons
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 201 else {
        throw APIError.serverError
    }
    return try decoder.decode(UserResponse.self, from: data)
}
```

## Good Example

```swift
// ✅ GOOD: Separation of infrastructure and business errors
enum APIError: Error {
    // Infrastructure
    case noConnection
    case timeout
    case networkError(URLError)

    // Business
    case serverError(statusCode: Int, body: ErrorResponse?)
    case decodingError(DecodingError)
    case invalidResponse
}

func createUser(_ request: CreateUserRequest) async throws -> UserResponse {
    let data: Data
    let response: URLResponse

    do {
        (data, response) = try await session.data(for: buildRequest(request))
    } catch let urlError as URLError {
        switch urlError.code {
        case .notConnectedToInternet, .networkConnectionLost:
            throw APIError.noConnection
        case .timedOut:
            throw APIError.timeout
        default:
            throw APIError.networkError(urlError)
        }
    }

    guard let httpResponse = response as? HTTPURLResponse else {
        throw APIError.invalidResponse
    }

    guard httpResponse.statusCode == 201 else {
        let errorBody = try? decoder.decode(ErrorResponse.self, from: data)
        throw APIError.serverError(statusCode: httpResponse.statusCode, body: errorBody)
    }

    do {
        return try decoder.decode(UserResponse.self, from: data)
    } catch let error as DecodingError {
        throw APIError.decodingError(error)
    }
}

// ✅ GOOD: UI distinguishes between error types
func handleError(_ error: Error) {
    switch error {
    case APIError.noConnection:
        showNoConnectionBanner()
    case APIError.timeout:
        showRetryDialog()
    case let APIError.serverError(_, body):
        showServerError(body?.message)
    default:
        showGenericError()
    }
}
```

## What to look for in code review

- `try await session.data(for:)` without catch `URLError`
- Single `APIError.unknown` for all error types
- UI shows the same message for network error and server error
- Lack of NWPathMonitor / connectivity check
- `URLError` in crash logs without turning into a domain error
