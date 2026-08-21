# Prefer Value Types (struct > class)

**Applies to:** Data models, services without identity, auxiliary types

## Why this matters

Prefer struct over class:
- Value semantics - copying on assignment, no shared mutable state
- No ARC overhead (retain/release) - faster allocation and deallocation
- Thread safety out of the box - each thread works with its own copy
- Automatic Sendable for struct with Sendable fields
- Stack allocation for small structs - faster than heap

## Bad Example

```swift
// ❌ BAD: class for a simple data model
class UserProfile {
    var name: String
    var email: String
    var age: Int

    init(name: String, email: String, age: Int) {
        self.name = name
        self.email = email
        self.age = age
    }
}

// Problem: shared reference
let profile = UserProfile(name: "Alice", email: "a@b.com", age: 30)
let copy = profile
copy.name = "Bob" // profile.name also became "Bob"!

// ❌ BAD: class for configuration
class APIConfig {
    var baseURL: URL
    var timeout: TimeInterval
    // ...
}
```

## Good Example

```swift
// ✅ GOOD: struct for the data model
struct UserProfile: Sendable {
    let name: String
    let email: String
    let age: Int
}

// Safe: value semantics
let profile = UserProfile(name: "Alice", email: "a@b.com", age: 30)
var copy = profile
copy = UserProfile(name: "Bob", email: copy.email, age: copy.age)
// profile.name is still "Alice"

// ✅ GOOD: struct for configuration
struct APIConfig: Sendable {
    let baseURL: URL
    let timeout: TimeInterval
}

// ✅ Exception: class is needed for identity, inheritance or reference semantics
final class DatabaseConnection {
    // Manages the resource - identity is important
    private let handle: OpaquePointer

    deinit {
        sqlite3_close(handle)
    }
}
```

## What to look for in code review

- `class` for data models (DTO, response, config) - replace with `struct`
- `class` without `deinit`, inheritance or reference identity - a candidate for struct
- Shared mutable state via class reference - potential data race
