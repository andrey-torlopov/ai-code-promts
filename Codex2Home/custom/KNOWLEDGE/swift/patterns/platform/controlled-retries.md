# Controlled Retries

**Applies to:** Networking, async operations

## Why this is bad

Uncontrolled retry logic:
- Endless retry hides real bugs
- Retry without backoff overloads the server and battery
- Retry all errors mask non-retriable failures (400, 403)
- User waits without feedback

## Bad Example

```swift
// ❌ BAD: Retry all errors, masks bugs
func createUserWithRetry(_ request: CreateUserRequest) async throws -> UserResponse {
    for attempt in 0..<5 {
        do {
            return try await apiClient.createUser(request)
        } catch {
            // Swallows all errors, including 400 Bad Request
            try? await Task.sleep(for: .seconds(1))
        }
    }
    throw APIError.maxRetriesExceeded
}

// ❌ BAD: Retry without distinguishing error types
func fetchData() async throws -> Data {
    var lastError: Error?
    for _ in 0..<3 {
        do {
            return try await session.data(for: request).0
        } catch {
            lastError = error
        }
    }
    throw lastError ?? APIError.unknown
}
```

## Good Example

```swift
// ✅ GOOD: Retry only for retriable errors with exponential backoff
func fetchWithRetry<T>(
    maxAttempts: Int = 3,
    initialDelay: Duration = .seconds(1),
    operation: () async throws -> T
) async throws -> T {
    var lastError: Error?

    for attempt in 0..<maxAttempts {
        do {
            return try await operation()
        } catch let error as URLError where error.isRetriable {
            lastError = error
            let delay = initialDelay * pow(2, Double(attempt))
            try await Task.sleep(for: delay)
        } catch {
            throw error // Non-retriable - throw immediately
        }
    }

    throw lastError ?? APIError.maxRetriesExceeded
}

extension URLError {
    var isRetriable: Bool {
        switch code {
        case .timedOut, .networkConnectionLost, .notConnectedToInternet:
            return true
        default:
            return false
        }
    }
}

// ✅ GOOD: Sync operations without retry - if it crashes, it's a bug
func createUser(_ request: CreateUserRequest) async throws -> UserResponse {
    try await apiClient.createUser(request)
}
```

## What to look for in code review

- `for _ in 0..<N` around async calls
- `catch { }` with empty body (swallowing errors)
- Retry without distinction between retriable (5xx, timeout) and non-retriable (4xx) errors
- No exponential backoff during retry
- Retry for synchronous CRUD operations (not async status polling)
