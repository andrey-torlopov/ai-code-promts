# String Search in Collection via Concatenation

**Applies to:** Performance, collections, search

## Why this is bad

Finding a string inside a large concatenated string instead of data structures:
- Linear substring search: ~200 ms in a real case
- Replacement with Set: ~2 ms (100x speedup)
- “I collected everything in a String and am looking for contains” - almost always an antipattern
- O(n*m) instead of O(1) when using a hash table

## Bad Example

```swift
// ❌ BAD: Search via contains in a merged string
final class FeatureRegistry {
    private var allFeatures: String = ""

    func register(_ feature: String) {
        allFeatures += "|\(feature)"
    }

    func isEnabled(_ feature: String) -> Bool {
        return allFeatures.contains(feature) // O(n*m)
    }
}

// ❌ BAD: Linear search in an array of strings
func findUser(by email: String, in users: [String]) -> Bool {
    return users.contains(email) // O(n)
}
```

## Good Example

```swift
// ✅ GOOD: Set for O(1) search
final class FeatureRegistry {
    private var features: Set<String> = []

    func register(_ feature: String) {
        features.insert(feature)
    }

    func isEnabled(_ feature: String) -> Bool {
        return features.contains(feature) // O(1)
    }
}

// ✅ GOOD: Dictionary for searching with associated data
struct UserLookup {
    private var usersByEmail: [String: User] = [:]

    mutating func add(_ user: User) {
        usersByEmail[user.email] = user
    }

    func find(by email: String) -> User? {
        return usersByEmail[email] // O(1)
    }
}

// ✅ GOOD: Hash suffixes for quick matching
struct SuffixMatcher {
    private var suffixMap: [String: [String]] = [:]

    mutating func add(_ value: String, suffixLength: Int = 4) {
        let suffix = String(value.suffix(suffixLength))
        suffixMap[suffix, default: []].append(value)
    }

    func matches(for suffix: String) -> [String] {
        return suffixMap[suffix] ?? []
    }
}
```

## What to look for in code review

- `bigString.contains(substring)` to search the collection of values
- Array of strings + `contains` / `first(where:)` ​​for frequent lookups
- String concatenation as a way to store a collection
- `joined(separator:)` + subsequent `contains` ​​/ `range(of:)`
