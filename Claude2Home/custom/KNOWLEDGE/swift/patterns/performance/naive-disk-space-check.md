# Naive Disk Space Check

**Applies to:** FileManager, disk space, app startup

## Why this is bad

Recalculating free space without caching:
- `attributesOfFileSystem` takes 400-850 ms per call
- At startup can be called 3-4 times by different components
- In total this is 1-3 seconds of lost start time
- The value does not change in seconds - there is no point in recalculating

## Bad Example

```swift
// ❌ BAD: Each call goes to the file system
final class StorageManager {
    func freeSpace() throws -> Int64 {
        let attrs = try FileManager.default.attributesOfFileSystem(
            forPath: NSHomeDirectory()
        )
        return attrs[.systemFreeSize] as? Int64 ?? 0
    }
}

// Called on every screen
let free = try storageManager.freeSpace() // 400-850 ms
```

## Good Example

```swift
// ✅ GOOD: Caching with TTL via actor
actor DiskSpaceService {
    private var cachedFreeSpace: Int64?
    private var lastCheck: Date = .distantPast
    private let ttl: TimeInterval = 300 // 5 minutes

    func freeSpace() throws -> Int64 {
        if let cached = cachedFreeSpace,
           Date().timeIntervalSince(lastCheck) < ttl {
            return cached
        }

        let url = URL(fileURLWithPath: NSHomeDirectory())
        let values = try url.resourceValues(forKeys: [.volumeAvailableCapacityForImportantUsageKey])
        let free = values.volumeAvailableCapacityForImportantUsage ?? 0

        cachedFreeSpace = free
        lastCheck = Date()
        return free
    }

    func invalidate() {
        cachedFreeSpace = nil
    }
}
```

## What to look for in code review

- `attributesOfFileSystem(forPath:)` without caching the result
- Multiple calls to check free space at startup
- `NSHomeDirectory()` + `attributesOfItem(atPath:)` ​​to get the size
- No TTL/memoization for disk metrics
