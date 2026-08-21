# String Operations in Hot Path

**Applies to:** Performance, crypto, security, parsing

## Why this is bad

String operations in performance critical areas:
- Creating a String from UTF-8 is expensive (validation, copying, ARC)
- String indexing takes into account grapheme clusters - not O(1)
- String comparisons are significantly more expensive than byte comparisons
- In the T-Bank case, the transition String -> [UInt8] gave an acceleration of up to 400x

## Bad Example

```swift
// ❌ BAD: Comparing tokens/hashes via strings
func verifyToken(_ token: String, expected: String) -> Bool {
    return token == expected
}

// ❌ BAD: Character-by-character processing via String.Index
func parseProtocol(_ input: String) -> [String] {
    var result: [String] = []
    var index = input.startIndex
    while index < input.endIndex {
        // O(n) for each index access
        let char = input[index]
        // ...
        index = input.index(after: index)
    }
    return result
}

// ❌ BAD: String concatenation to construct binary data
func buildPayload(parts: [String]) -> String {
    return parts.joined(separator: "|")
}
```

## Good Example

```swift
// ✅ GOOD: Comparison via byte arrays
func verifyToken(_ token: Data, expected: Data) -> Bool {
    guard token.count == expected.count else { return false }
    // Constant-time comparison for security
    var result: UInt8 = 0
    for i in 0..<token.count {
        result |= token[i] ^ expected[i]
    }
    return result == 0
}

// ✅ GOOD: Parsing via UTF8View or [UInt8]
func parseProtocol(_ input: String) -> [ArraySlice<UInt8>] {
    let bytes = Array(input.utf8)
    var result: [ArraySlice<UInt8>] = []
    var start = 0
    for i in 0..<bytes.count {
        if bytes[i] == UInt8(ascii: "|") {
            result.append(bytes[start..<i])
            start = i + 1
        }
    }
    if start < bytes.count {
        result.append(bytes[start..<bytes.count])
    }
    return result
}

// ✅ GOOD: Data for binary operations
func buildPayload(parts: [Data]) -> Data {
    var payload = Data()
    for (i, part) in parts.enumerated() {
        if i > 0 { payload.append(UInt8(ascii: "|")) }
        payload.append(part)
    }
    return payload
}
```

## What to look for in code review

- Comparison of secrets (tokens, hashes, keys) via `String ==`
- Cycles by `String.Index` in the hot path
- `String(data:encoding:)` in tight loop
- String concatenation for binary protocols
- Frequent creation/destruction of large String objects
