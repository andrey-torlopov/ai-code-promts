# No Hardcoded Timeouts

**Applies to:** Networking, tests, polling

## Why this is bad

Hardcoded timeouts in the code:
- Breaks on slow CI (timeout is too small)
- Waste time on fast environments (timeout is too long)
- Cannot be overridden for different environments (debug/staging/prod)
- Magic numbers are scattered throughout the project

## Bad Example

```swift
// ❌ BAD: Magic numbers in tests
func testAsyncOperation() async throws {
    let expectation = expectation(description: "Done")
    await fulfillment(of: [expectation], timeout: 5)
}

// ❌ BAD: Different timeouts in different places
try await waitUntil(timeout: .seconds(3)) { /* ... */ }
try await waitUntil(timeout: .seconds(10)) { /* ... */ }
try await waitUntil(timeout: .seconds(30)) { /* ... */ }

// ❌ BAD: Hardcode of timeouts in networking
var request = URLRequest(url: url)
request.timeoutInterval = 15 // Why 15? For what environment?
```

## Good Example

```swift
// ✅ GOOD: Timeouts in the configuration, reused
enum TestConfig {
    static let defaultPollingTimeout: Duration = {
        let seconds = ProcessInfo.processInfo.environment["POLL_TIMEOUT_SEC"]
            .flatMap(Double.init) ?? 10
        return .seconds(seconds)
    }()

    static let defaultPollingInterval: Duration = .seconds(1)

    static let expectationTimeout: TimeInterval = {
        ProcessInfo.processInfo.environment["EXPECTATION_TIMEOUT_SEC"]
            .flatMap(TimeInterval.init) ?? 5
    }()
}

// Usage
try await waitUntil(
    timeout: TestConfig.defaultPollingTimeout,
    pollInterval: TestConfig.defaultPollingInterval
) {
    let response = try await apiClient.getUser(userId)
    return response.body.status == "active"
}

await fulfillment(of: [expectation], timeout: TestConfig.expectationTimeout)
```

## What to look for in code review

- `timeout:` with literal numbers in tests and production code
- Different timeouts for the same operations in different places
- Lack of centralized timeout config
- `.seconds(N)`, `.milliseconds(N)` ​​without explanation “why this value”
