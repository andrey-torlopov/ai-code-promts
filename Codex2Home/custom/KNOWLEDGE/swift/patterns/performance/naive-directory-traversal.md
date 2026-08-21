# Naive Directory Traversal

**Applies to:** FileManager, file enumeration, directory scanning

## Why this is bad

Recursive directory traversal without optimization:
- Naive implementation: ~3.3 seconds on a typical file tree
- Optimized: ~160 ms (20x speedup)
- Each `attributesOfItem` is a separate syscall
- Without prefetch keys, each `resourceValues` goes to FS again

## Bad Example

```swift
// ❌ BAD: Recursive traversal with attributesOfItem for each file
func calculateSize(at path: String) throws -> Int64 {
    let contents = try FileManager.default.subpathsOfDirectory(atPath: path)
    var total: Int64 = 0
    for subpath in contents {
        let fullPath = (path as NSString).appendingPathComponent(subpath)
        let attrs = try FileManager.default.attributesOfItem(atPath: fullPath)
        if let type = attrs[.type] as? FileAttributeType,
           type == .typeRegular {
            total += attrs[.size] as? Int64 ?? 0
        }
    }
    return total
}
```

## Good Example

```swift
// ✅ GOOD: enumerator with includingPropertiesForKeys for prefetch
func calculateSize(at directory: URL) throws -> Int64 {
    let keys: Set<URLResourceKey> = [.fileSizeKey, .isRegularFileKey]

    guard let enumerator = FileManager.default.enumerator(
        at: directory,
        includingPropertiesForKeys: Array(keys),
        options: [.skipsHiddenFiles],
        errorHandler: { url, error in
            // Log, but continue traversing
            false
        }
    ) else {
        return 0
    }

    var total: Int64 = 0
    for case let url as URL in enumerator {
        // resourceValues ​​are taken from the cache thanks to includingPropertiesForKeys
        let values = try url.resourceValues(forKeys: keys)
        if values.isRegularFile == true {
            total += Int64(values.fileSize ?? 0)
        }
    }
    return total
}
```

## What to look for in code review

- `subpathsOfDirectory(atPath:)` + piece `attributesOfItem`
- `enumerator` without `includingPropertiesForKeys` ​​(missing prefetch)
- `contentsOfDirectory` + manual recursion instead of `enumerator`
- Traversing large directories in the main thread
