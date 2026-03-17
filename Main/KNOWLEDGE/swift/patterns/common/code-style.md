# Code Style

**Applies to:** All Swift code of the project

## Rules

- Do not use "—" (em dash and hyphens) in comments - use "-"
- Don't add comments to obvious code
- Do not add `// MARK:` without asking
- Don't add docstrings without asking
- Don't wrap code in `#if DEBUG` without prompting

## Bad Example

```swift
// ❌ BAD: unnecessary comments, MARK, docstrings, em dash
// MARK: - Properties

/// Loads data from the network
func loadData() async throws -> Data {
    // Create a URL - form a request
    let url = URL(string: endpoint)!
    #if DEBUG
    print("loading...")
    #endif
    // Return the result
    return try await URLSession.shared.data(from: url).0
}
```

## Good Example

```swift
// ✅ GOOD: only necessary comments, no MARK/docstrings without request
func loadData() async throws -> Data {
    let url = URL(string: endpoint)!
    return try await URLSession.shared.data(from: url).0
}
```

## What to look for in code review

- "—" (em dash) in comments instead of "-"
- Comments duplicating obvious code
- `// MARK:` added without an explicit request
- Docstrings added without explicit request
- `#if DEBUG` wrappers added without an explicit request
