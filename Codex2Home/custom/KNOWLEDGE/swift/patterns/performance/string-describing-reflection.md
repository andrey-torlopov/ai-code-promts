# String(describing:) and Reflection

**Applies to:** Performance, logging, app startup

## Why this is bad

`String(describing:)` (String Scrubbing) causes many castes to protocols:
- For a simple structure without fields - 4 casts via `swift_conform_protocol`
- With each field the number of castes grows
- At the start of the T-Bank application it took ~250 ms
- The result depends on the `Swift Reflection Level` flag - non-deterministic output
- Refusal from String Scrubbing gave: -5% start, -12% preparation of the main screen, -7% loading

## Bad Example

```swift
// ❌ BAD: String(describing:) for the type name
func logEvent<T>(_ value: T) {
    let typeName = String(describing: type(of: value))
    logger.info("Processing \(typeName)")
}

// ❌ BAD: Interpolate T.self (causes String Scrubbing)
func register<T>(_ type: T.Type) {
    let key = "\(T.self)"
    registry[key] = Factory<T>()
}

// ❌ BAD: String(describing:) for the value
func cacheKey(for value: some Hashable) -> String {
    return String(describing: value)
}
```

## Good Example

```swift
// ✅ GOOD: _typeName for the type name (without reflection)
func logEvent<T>(_ value: T) {
    let typeName = _typeName(type(of: value))
    logger.info("Processing \(typeName)")
}

// ✅ GOOD: ObjectIdentifier to identify the type
func register<T>(_ type: T.Type) {
    let key = ObjectIdentifier(T.self)
    registry[key] = Factory<T>()
}

// ✅ GOOD: CustomStringConvertible for controlled output
struct CacheEntry: CustomStringConvertible {
    let id: String
    let timestamp: Date

    var description: String {
        "CacheEntry(\(id))"
    }
}

func cacheKey(for value: CacheEntry) -> String {
    return value.description
}
```

## What to look for in code review

- `String(describing:)` in hot mode or at the start
- `"\(T.self)"` or `"\(type(of: obj))"` ​​to identify types
- `String(describing:)` as a dictionary or cache key
- Lack of `CustomStringConvertible` when using string representation frequently
