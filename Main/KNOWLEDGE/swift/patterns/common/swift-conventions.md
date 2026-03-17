# Swift Conventions

**Applies to:** All Swift code of the project

## Rules

- Follow Swift API Design Guidelines
- Use `let` instead of `var` ​​where possible
- Prefer value types (struct, enum) over reference types (class) unless clearly necessary
- we use enum only if we plan to check transfers. Otherwise we use struct
- Use `async/await` instead of completion handlers
- Use Modern concurrency instead of NSLog, Semaphore and other mechanisms
- Use structured concurrency (TaskGroup, async let) instead of unstructured Task {}
- Mark types as `Sendable` where possible
- Use `@MainActor` for UI code, not `DispatchQueue.main`
- Handle errors via `throws` / `Result`, not via optionals for error states
- Use `guard` for early exit
- In Task, if we use [weak self], then we do not strengthen self immediately, but only before using it for the first time
- Prefer `[weak self]` in escaping closures to prevent retain cycles
- Do not use force unwrap (`!`) except for IBOutlet and tests
- Don't use `Any` / `AnyObject` ​​unless absolutely necessary - prefer protocols and generics
- We try not to use Task.detached()
- We try not to use .init, but an explicit indication of the class/structure

## Bad Example

```swift
// ❌ BAD: completion handler, force unwrap, var, DispatchQueue
class DataManager {
    var result: String? = nil

    func loadData(completion: @escaping (String?) -> Void) {
        DispatchQueue.global().async {
            let data = self.fetchFromNetwork()
            DispatchQueue.main.async {
                self.result = data
                completion(data)
            }
        }
    }

    func process() {
        let value = result!
        print(value)
    }
}
```

## Good Example

```swift
// ✅ GOOD: async/await, @MainActor, let, guard, Sendable
@MainActor
final class DataManager: Sendable {
    let repository: DataRepository

    func loadData() async throws -> String {
        let data = try await repository.fetch()
        return data
    }

    func process() throws {
        guard let value = optionalResult else { return }
        print(value)
    }
}
```

## What to look for in code review

- `var` where you can use `let`
- `class` where `struct` ​​is sufficient
- completion handlers instead of async/await
- `DispatchQueue.main` instead of `@MainActor`
- `Task {}` instead of structured concurrency (TaskGroup, async let)
- `Task.detached()` without explicit need
- Force unwrap (`!`) outside IBOutlet/tests
- `Any` / `AnyObject` ​​instead of protocols/generics
- `.init(...)` instead of explicit `TypeName(...)`
- Options for error states instead of throws/Result
