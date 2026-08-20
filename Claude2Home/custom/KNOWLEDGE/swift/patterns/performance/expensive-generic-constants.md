# Expensive Generic Constants

**Applies to:** Performance, generics, app startup

## Why this is bad

Swift creates metadata for generic types at runtime:
- `swift_checkGenericRequirements` calls `swift_conform_protocol` ​​for each protocol constraint
- Generic constants in reused components are especially expensive
- Saving the size of metadata in a binary leads to additional CPU costs
- In T-Bank, eliminating generic constants speeded up the start by 11% (220 ms) and the preparation of the main page by 10% (95 ms)

## Bad Example

```swift
// ❌ BAD: Generic constant for decoding
struct Feature<T: Decodable> {
    let decoder: JSONDecoder
    let type: T.Type

    func decode(from data: Data) throws -> T {
        try decoder.decode(T.self, from: data)
    }
}

// Each creation Feature<X> -> swift_checkGenericRequirements
let featureA = Feature<ConfigA>(decoder: decoder, type: ConfigA.self)
let featureB = Feature<ConfigB>(decoder: decoder, type: ConfigB.self)
// ...dozens of such registrations at the start
```

## Good Example

```swift
// ✅ GOOD: Decode/encode injection via closure instead of generic
struct Feature {
    let decode: (Data) throws -> Any

    init<T: Decodable>(type: T.Type, decoder: JSONDecoder = JSONDecoder()) {
        self.decode = { data in
            try decoder.decode(T.self, from: data)
        }
    }
}

// The generic is used only in init, not in the stored type
let featureA = Feature(type: ConfigA.self)
let featureB = Feature(type: ConfigB.self)
```

## What to look for in code review

- Generic structures/classes with protocol restrictions, created in bulk
- Mass registration of generic components at the start of the application
- Generic parameters that can be replaced with closures or type erasure
- `where T: ProtocolA & ProtocolB & ProtocolC` - each protocol is checked separately
