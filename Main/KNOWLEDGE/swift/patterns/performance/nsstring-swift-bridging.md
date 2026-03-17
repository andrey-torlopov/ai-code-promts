# NSString-Swift String Bridging in Tight Loop

**Applies to:** Performance, Objective-C interop, bridging

## Why this is bad

Frequent NSString <-> String conversions in the hot way:
- Each bridging cast creates a copy or increases the refcount
- In a tight loop this noticeably impacts performance
- Mixing NSString and String API in one code block - double costs
- Especially critical when working with legacy Obj-C libraries

## Bad Example

```swift
// ❌ BAD: Constant transitions NSString <-> String
func processItems(_ items: [NSString]) -> [String] {
    return items.map { nsString in
        let swiftString = nsString as String         // bridging
        let modified = swiftString.lowercased()
        let nsModified = modified as NSString // bridging back
        let range = nsModified.range(of: "pattern")
        let result = nsModified.substring(from: range.location) // NSString API
        return result as String // and bridging again
    }
}

// ❌ BAD: Using NSString API on Swift String
func extractComponent(_ path: String) -> String {
    return (path as NSString).lastPathComponent // bridging for one call
}
```

## Good Example

```swift
// ✅ GOOD: Work completely in one world
func processItems(_ items: [NSString]) -> [String] {
    // Convert once, then we work only with Swift
    let swiftItems = items.map { $0 as String }
    return swiftItems.map { string in
        let modified = string.lowercased()
        guard let range = modified.range(of: "pattern") else { return modified }
        return String(modified[range.lowerBound...])
    }
}

// ✅ GOOD: URL API instead of NSString path manipulation
func extractComponent(_ url: URL) -> String {
    return url.lastPathComponent
}

// ✅ GOOD: If you need an Obj-C block, keep it entirely in NSString
func processLegacy(_ items: [NSString]) -> [NSString] {
    return items.map { nsString in
        // Entire block on NSString, no switches
        let range = nsString.range(of: "pattern")
        guard range.location != NSNotFound else { return nsString }
        return nsString.substring(from: range.location) as NSString
    }
}
```

## What to look for in code review

- `as NSString` / `as String` ​​in a loop or map/filter/reduce
- Alternating Swift String methods and NSString methods in one block
- `(path as NSString).lastPathComponent` - replace with URL
- Legacy Obj-C API calls mixed with Swift string processing
