# No Shared Mutable State

**Applies to:** Tests, multi-threaded code

## Why this is bad

Shared mutable state between tests or threads:
- Tests depend on the order of execution
- Parallel launch breaks everything
- Data race with concurrent access
- The failure of one test cascadingly breaks the next ones

## Bad Example

```swift
// ❌ BAD: Static var in the test class - tests depend on each other
class UserTests: XCTestCase {
    static var createdUserId: String = ""

    override class func setUp() {
        super.setUp()
        createdUserId = createUser()
    }

    func testUpdateUser() async throws {
        let response = try await apiClient.updateUser(Self.createdUserId, newData)
        XCTAssertEqual(response.statusCode, 200, "Update should succeed")
    }

    func testDeleteUser() async throws {
        let response = try await apiClient.deleteUser(Self.createdUserId)
        XCTAssertEqual(response.statusCode, 204, "Delete should succeed")
        // After delete - testUpdateUser will break
    }
}

// ❌ BAD: Shared mutable state in production code without synchronization
class UserCache {
    var users: [String: User] = [:] // Data race for concurrent access

    func getUser(_ id: String) -> User? {
        users[id] // Read without synchronization
    }

    func setUser(_ user: User) {
        users[user.id] = user // Record without synchronization
    }
}
```

## Good Example

```swift
// ✅ GOOD: Each test creates its own data
class UserTests: XCTestCase {
    func testUpdateUser() async throws {
        let userId = try await UserHelper.createUser(TestData.validCreateBody())

        let response = try await apiClient.updateUser(userId, TestData.validUpdateBody())
        XCTAssertEqual(response.statusCode, 200, "Update should succeed")
    }

    func testDeleteUser() async throws {
        let userId = try await UserHelper.createUser(TestData.validCreateBody())

        let response = try await apiClient.deleteUser(userId)
        XCTAssertEqual(response.statusCode, 204, "Delete should succeed")
    }
}

// ✅ GOOD: Actor for thread-safe shared state
actor UserCache {
    private var users: [String: User] = [:]

    func getUser(_ id: String) -> User? {
        users[id]
    }

    func setUser(_ user: User) {
        users[user.id] = user
    }
}

// ✅ GOOD: Sendable struct for immutable shared data
struct AppConfig: Sendable {
    let baseURL: URL
    let apiKey: String
    let timeout: TimeInterval
}
```

## What to look for in code review

- `static var` in XCTestCase (except lazy configuration)
- Test A creates data, test B uses it
- `var` properties in classes without `actor` ​​or synchronization
- Lack of `Sendable` conformance for types passed between threads
- `@unchecked Sendable` without justification
- `DispatchQueue` for synchronization instead of `actor` ​​(legacy)
