# NSDictionary File Attributes

**Applies to:** FileManager, file metadata, URL resources

## Why this is bad

Using the old NSDictionary API for file attributes:
- `attributesOfItem(atPath:)` returns a dictionary with ALL attributes
- Excessive CPU and memory work when 1-2 values ​​are needed
- String-based paths are more expensive than URL-based ones for bulk operations
- No attribute caching, every call goes to FS

## Bad Example

```swift
// ❌ BAD: Full attribute dictionary via old API
func fileSize(at path: String) throws -> Int64 {
    let attrs = try FileManager.default.attributesOfItem(atPath: path)
    return attrs[.size] as? Int64 ?? 0
}

// ❌ BAD: String paths in bulk operations
func totalSize(of directory: String) throws -> Int64 {
    let contents = try FileManager.default.contentsOfDirectory(atPath: directory)
    return try contents.reduce(0) { total, name in
        let fullPath = (directory as NSString).appendingPathComponent(name)
        let attrs = try FileManager.default.attributesOfItem(atPath: fullPath)
        return total + (attrs[.size] as? Int64 ?? 0)
    }
}
```

## Good Example

```swift
// ✅ GOOD: URL + resourceValues ​​- request only the necessary keys
func fileSize(at url: URL) throws -> Int64 {
    let values = try url.resourceValues(forKeys: [.fileSizeKey])
    return Int64(values.fileSize ?? 0)
}

// ✅ GOOD: enumerator with prefetch of the necessary keys
func totalSize(of directory: URL) throws -> Int64 {
    guard let enumerator = FileManager.default.enumerator(
        at: directory,
        includingPropertiesForKeys: [.fileSizeKey, .isRegularFileKey],
        options: [.skipsHiddenFiles]
    ) else {
        return 0
    }

    var total: Int64 = 0
    for case let fileURL as URL in enumerator {
        let values = try fileURL.resourceValues(forKeys: [.fileSizeKey, .isRegularFileKey])
        if values.isRegularFile == true {
            total += Int64(values.fileSize ?? 0)
        }
    }
    return total
}
```

## What to look for in code review

- `attributesOfItem(atPath:)` - replace with `url.resourceValues(forKeys:)`
- `NSString.appendingPathComponent` - replace with `URL.appending(path:)`
- `contentsOfDirectory(atPath:)` - replace with `enumerator(at:includingPropertiesForKeys:)`
- `FileManager` calls without `includingPropertiesForKeys`
- Work with paths through `String` instead of `URL`
