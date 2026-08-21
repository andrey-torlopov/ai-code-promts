# Prefer final class

**Applies to:** All classes in production and test code

## Why this matters

Mark `final` for classes that are not intended to be inherited:
- The compiler uses static dispatch instead of dynamic dispatch - calling methods is faster
- Explicitly expresses the intent: "this class is not for inheritance"
- Prevents accidental inheritance and fragile hierarchies
- Compatible with Sendable (final class is easier to make Sendable)

## Bad Example

```swift
// ❌ BAD: Class without final - it is unclear whether inheritance is planned
class NetworkService {
    let session: URLSession

    init(session: URLSession = .shared) {
        self.session = session
    }

    func fetch(_ url: URL) async throws -> Data {
        let (data, _) = try await session.data(from: url)
        return data
    }
}

// ❌ BAD: ViewModel without final - dynamic dispatch for each call
class ProfileViewModel: ObservableObject {
    @Published var name: String = ""

    func load() async { /* ... */ }
}
```

## Good Example

```swift
// ✅ GOOD: final - explicit intent, static dispatch
final class NetworkService {
    let session: URLSession

    init(session: URLSession = .shared) {
        self.session = session
    }

    func fetch(_ url: URL) async throws -> Data {
        let (data, _) = try await session.data(from: url)
        return data
    }
}

// ✅ GOOD: final + Sendable
final class ProfileViewModel: ObservableObject, Sendable {
    @Published var name: String = ""

    func load() async { /* ... */ }
}

// ✅ Exception: the class is INTENTIONALLY created for inheritance
class BaseCoordinator {
    func start() {
        // Override point for heirs
    }
}
```

## What to look for in code review

- `class` without `final` ​​- ask: is inheritance planned?
- If there are no heirs and there are no plans, add `final`
- `open class` in a module without external consumers
