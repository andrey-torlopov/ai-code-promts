# Anti-Pattern: Async Test Pitfalls

## Problem

Incorrect use of async/await in XCTest results in tests that fail,
but do not test what is expected - or freeze without diagnostics.

## Bad Example

```swift
// ❌ BAD: Fire-and-forget Task in the test - the test completes before the check
func testUserCreation() {
    Task {
        let response = try await apiClient.createUser(request)
        XCTAssertEqual(response.statusCode, 201) // May fail
    }
    // The test completes immediately, without waiting for the Task
}

// ❌ BAD: XCTestExpectation for async code (legacy approach)
func testUserCreation() {
    let expectation = expectation(description: "User created")

    Task {
        let response = try await apiClient.createUser(request)
        XCTAssertEqual(response.statusCode, 201)
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 5)
}

// ❌ BAD: DispatchSemaphore blocks main thread
func testUserCreation() {
    let semaphore = DispatchSemaphore(value: 0)
    Task {
        let response = try await apiClient.createUser(request)
        XCTAssertEqual(response.statusCode, 201)
        semaphore.signal()
    }
    semaphore.wait()
}
```

## Good Example

```swift
// ✅ GOOD: async test method (Swift 5.5+, Xcode 13+)
func testUserCreation() async throws {
    let response = try await apiClient.createUser(request)
    XCTAssertEqual(response.statusCode, 201, "User creation should succeed")
}

// ✅ GOOD: Structured concurrency in the test
func testParallelRequests() async throws {
    async let userResponse = apiClient.createUser(userRequest)
    async let profileResponse = apiClient.createProfile(profileRequest)

    let (user, profile) = try await (userResponse, profileResponse)
    XCTAssertEqual(user.statusCode, 201, "User should be created")
    XCTAssertEqual(profile.statusCode, 201, "Profile should be created")
}
```

## Why

- `Task { }` in sync test creates unstructured concurrency - the test does not wait for completion
- `XCTestExpectation` for async code - legacy pattern, async test methods cleaner
- `DispatchSemaphore` can block cooperative thread pool Swift concurrency
- `async throws` test methods automatically wait for completion and throw errors

## Detection

```bash
grep -rn "Task {" --include="*Tests.swift" Tests/ | grep -v "addTeardownBlock"
grep -rn "DispatchSemaphore\|semaphore.wait" --include="*Tests.swift" Tests/
```

## References

- (ref: platform/async-test-pitfalls.md)
- Apple: Testing asynchronous code
