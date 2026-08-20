# Protocol Cast Over Class Cast

**Applies to:** Performance, app startup, swift_conform_protocol

## Why this is bad

Cast to protocol (`as? SomeProtocol`) calls `swift_conform_protocol`:
- Linear search over all conformances when cache misses (~130k in large applications)
- The first cast to the protocol is the most difficult, then the cache works
- `is SomeProtocol` same expensive - same linear search
- Cast to array (`as? [SomeProtocol]`) checks each element
- In T-Bank, replacing castes for protocols with castes for classes gave -20% start and -40% preparation of the main screen

Cast to class (`as? SomeClass`) - fast check of ISA pointer, O(1).

## Bad Example

```swift
// ❌ BAD: Cast to the protocol in the hot way
protocol Configurable {
    func configure()
}

func process(items: [Any]) {
    for item in items {
        // swift_conform_protocol at each iteration
        if let configurable = item as? Configurable {
            configurable.configure()
        }
    }
}

// ❌ BAD: Checking is with protocol
func shouldProcess(_ item: Any) -> Bool {
    return item is Configurable // linear search for conformations
}

// ❌ BAD: Cast an array to a protocol type
let items: [Any] = loadItems()
if let configurables = items as? [Configurable] {
    // Check each element
}
```

## Good Example

```swift
// ✅ GOOD: Cast to the base class - O(1) via ISA pointer
class BaseConfigurable {
    func configure() {}
}

func process(items: [Any]) {
    for item in items {
        if let configurable = item as? BaseConfigurable {
            configurable.configure()
        }
    }
}

// ✅ GOOD: Caching the cast result if the protocol is unavoidable
func processOnce(item: Any) {
    // One cast, the result is saved
    guard let configurable = item as? Configurable else { return }
    configurable.configure()
    configurable.validate()
    configurable.apply()
}

// ✅ GOOD: Using generics instead of casts
func process<T: Configurable>(_ item: T) {
    item.configure()
}
```

## Exceptions

- `@objc` protocols - do not require `swift_conform_protocol`
- Marker protocols (`Sendable`) - compile-time check
- Inlining protocol witness table for specific types (only in Release)

## What to look for in code review

- `as? SomeProtocol` in cycles and on hot paths
- `is SomeProtocol` as a condition in frequently called code
- Cast arrays to protocol types (`as? [Protocol]`)
- Multiple castes of one object to different protocols
