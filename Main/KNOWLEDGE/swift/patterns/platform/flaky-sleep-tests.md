# Flaky Sleep Tests

## Why this is bad

`Thread.sleep()` / `Task.sleep()` ​​with fixed time creates unstable tests:
- On slow machines/CI the test crashes (timeout is too short)
- On fast machines the test wastes time
- It is impossible to predict how long an async operation will take

## Bad Example

```swift
// ❌ BAD: Magic number, flaky on slow CI
func testUserStatusBecomesActive() async throws {
    let userId = try await userHelper.registerUser(TestData.validRequest())

    try await Task.sleep(for: .seconds(2)) // Wait for "enough"

    let response = try await apiClient.getUser(userId)
    XCTAssertEqual(response.body.status, "active", "User should become active")
}

// ❌ BAD: Thread.sleep blocks the thread
func testNotificationReceived() {
    notificationService.send(notification)
    Thread.sleep(forTimeInterval: 1.0) // Blocks the cooperative thread pool
    XCTAssertTrue(handler.didReceive)
}
```

## Good Example

```swift
// ✅ GOOD: XCTestExpectation with polling for async status
func testUserStatusBecomesActive() async throws {
    let userId = try await userHelper.registerUser(TestData.validRequest())

    let predicate = NSPredicate { _, _ in
        let response = try? await self.apiClient.getUser(userId)
        return response?.body.status == "active"
    }

    let expectation = XCTNSPredicateExpectation(predicate: predicate, object: nil)
    await fulfillment(of: [expectation], timeout: 10)
}

// ✅ GOOD: Custom polling helper
func testUserStatusBecomesActive() async throws {
    let userId = try await userHelper.registerUser(TestData.validRequest())

    try await waitUntil(timeout: .seconds(10), pollInterval: .milliseconds(500)) {
        let response = try await apiClient.getUser(userId)
        return response.body.status == "active"
    }
}

// Reusable polling helper
func waitUntil(
    timeout: Duration,
    pollInterval: Duration = .seconds(1),
    condition: () async throws -> Bool
) async throws {
    let deadline = ContinuousClock.now + timeout
    while ContinuousClock.now < deadline {
        if try await condition() { return }
        try await Task.sleep(for: pollInterval)
    }
    XCTFail("Condition not met within \(timeout)")
}
```

## What to look for in code review

- `Thread.sleep()`, `Task.sleep(for:)` ​​with a fixed value in tests
- Magic numbers in timeouts without explanation
- Comments like "wait for async operation"
- Tests that “sometimes crash” (flaky)
- `usleep()`, `sleep()` ​​in test code
