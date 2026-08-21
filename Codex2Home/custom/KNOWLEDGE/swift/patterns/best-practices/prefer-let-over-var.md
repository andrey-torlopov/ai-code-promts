# Prefer let over var

**Applies to:** All variables in production and test code

## Why this matters

Using `let` by default:
- Immutability prevents random mutations
- The compiler can optimize immutable values
- It's easier to talk about data flow - the value doesn't change after initialization
- Helps with thread safety - immutable data is safe for concurrent access

## Bad Example

```swift
// ❌ BAD: var for a value that does not change
func processUser(_ user: User) {
    var name = user.displayName // never reassigned
    var url = URL(string: user.avatarURL) // never reassigned
    print(name)
    loadAvatar(from: url)
}

// ❌ BAD: var in closure parameters without mutation
let names = users.map { user -> String in
    var result = user.firstName + " " + user.lastName // does not mutate further
    return result
}
```

## Good Example

```swift
// ✅ GOOD: let for everything that does not require mutation
func processUser(_ user: User) {
    let name = user.displayName
    let url = URL(string: user.avatarURL)
    print(name)
    loadAvatar(from: url)
}

// ✅ GOOD: var only when the value actually changes
func buildFullName(parts: [String]) -> String {
    var result = "" // mutates in the loop - var is justified
    for (index, part) in parts.enumerated() {
        if index > 0 { result += " " }
        result += part
    }
    return result
}

// ✅ GOOD: let in closures
let names = users.map { user -> String in
    let result = user.firstName + " " + user.lastName
    return result
}
```

## What to look for in code review

- `var` without subsequent reassignment - replace with `let`
- Xcode warning "Variable was never mutated" - always fix
- `var` in guard/if let - check if mutation is needed
