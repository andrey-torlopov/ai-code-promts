# No Order-Dependent Tests

**Applies to:** Unit tests, Integration tests

## Why this is bad

Tests that depend on execution order:
- XCTest does not guarantee default order (randomization in Xcode)
- Parallel launch is not possible
- One failed test cascades down all the following ones

## Bad Example

```swift
// ❌ BAD: Tests are order dependent - delete doesn't work without create
class UserTests: XCTestCase {
    static var userId: String = ""

    func test1_createUser() async throws {
        let response = try await apiClient.createUser(TestData.validCreateBody())
        Self.userId = response.body.id
    }

    func test2_getUser() async throws {
        let response = try await apiClient.getUser(Self.userId)
        XCTAssertEqual(response.statusCode, 200, "Get user should return 200")
    }

    func test3_deleteUser() async throws {
        let response = try await apiClient.deleteUser(Self.userId)
        XCTAssertEqual(response.statusCode, 204, "Delete should return 204")
    }
}
```

## Good Example

```swift
// ✅ GOOD: Each test is completely autonomous
class UserTests: XCTestCase {

    func testGetUserById() async throws {
        let userId = try await UserHelper.createUser(TestData.validCreateBody())

        let response = try await apiClient.getUser(userId)
        XCTAssertEqual(response.statusCode, 200, "Get user should return 200")
    }

    func testDeleteUser() async throws {
        let userId = try await UserHelper.createUser(TestData.validCreateBody())

        let response = try await apiClient.deleteUser(userId)
        XCTAssertEqual(response.statusCode, 204, "Delete should return 204")
    }
}
```

## What to look for in code review

- Methods numbered `test1_`, `test2_`, `test3_`
- `static var` in XCTestCase, filled in one test
- Tests that crash when run individually
- Comments like "run after test X"
- Disabled test randomization in Xcode schema
