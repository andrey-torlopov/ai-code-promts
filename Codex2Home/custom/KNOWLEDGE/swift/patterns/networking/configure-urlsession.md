# Configure URLSession

**Applies to:** Networking layer, API clients

## Why this is bad

Default URLSession configuration in code:
- Default timeout (60 seconds) hangs UI and tests
- Default caching hides real problems
- Lack of limits on concurrent connections leads to resource exhaustion
- `URLSession.shared` does not allow customization of behavior for specific scenarios

## Bad Example

```swift
// ❌ BAD: Default session without timeouts
final class APIClient {
    let session = URLSession.shared
}

// ❌ BAD: The timeout is set differently in each request
func fetchSlowEndpoint() async throws -> Data {
    var request = URLRequest(url: slowURL)
    request.timeoutInterval = 30
    let (data, _) = try await session.data(for: request)
    return data
}
```

## Good Example

```swift
// ✅ GOOD: Centralized configuration
final class APIClient: Sendable {
    let session: URLSession

    init(configuration: APIConfiguration = APIConfiguration()) {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = configuration.requestTimeout
        config.timeoutIntervalForResource = configuration.resourceTimeout
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.httpMaximumConnectionsPerHost = configuration.maxConnectionsPerHost
        self.session = URLSession(configuration: config)
    }
}

struct APIConfiguration: Sendable {
    let baseURL: URL
    let requestTimeout: TimeInterval
    let resourceTimeout: TimeInterval
    let maxConnectionsPerHost: Int

    init(
        baseURL: URL = URL(string: "http://localhost:8080")!,
        requestTimeout: TimeInterval = 10,
        resourceTimeout: TimeInterval = 30,
        maxConnectionsPerHost: Int = 4
    ) {
        self.baseURL = baseURL
        self.requestTimeout = requestTimeout
        self.resourceTimeout = resourceTimeout
        self.maxConnectionsPerHost = maxConnectionsPerHost
    }
}
```

## What to look for in code review

- `URLSession.shared` in production code (not tests)
- `URLSessionConfiguration.default` without explicit timeouts
- `timeoutInterval` in the body of individual requests (not in the configuration)
- Different timeouts in different places for the same service
- Lack of `requestCachePolicy` (cache hides bugs)
