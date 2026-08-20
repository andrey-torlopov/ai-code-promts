# Naming Conventions

**Applies to:** All Swift code of the project

## Rules

- Types and protocols: UpperCamelCase
- Variables, functions, parameters: lowerCamelCase
- Protocol abilities: suffix -able/-ible (Sendable, Codable)
- Boolean properties: `isEnabled`, `hasContent`, `shouldReload`

## Bad Example

```swift
// ❌ BAD: Incorrect naming
protocol data_provider { }
struct user_model { }

let IsLoading = true
let enabled = false
func FetchData() { }
```

## Good Example

```swift
// ✅ GOOD: Swift API Design Guidelines
protocol DataProviding { }
protocol Cacheable { }
struct UserModel { }

let isLoading = true
let isEnabled = false
let hasContent = true
let shouldReload = false
func fetchData() { }
```

## What to look for in code review

- snake_case in type or function names
- Protocols-abilities without the suffix -able/-ible
- Boolean properties without is/has/should prefix
- UpperCamelCase in variable/function names
- lowerCamelCase in type/protocol names
