# Fix Patterns

Use this only after the user approves exact changes.

## Build Settings

Verify the target/configuration with `xcodebuild -showBuildSettings` after editing `project.pbxproj`.

Debug dSYM overhead:

```text
DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
```

Change to:

```text
DEBUG_INFORMATION_FORMAT = dwarf;
```

Debug compilation mode:

```text
SWIFT_COMPILATION_MODE = wholemodule;
```

Change to:

```text
SWIFT_COMPILATION_MODE = singlefile;
```

Compilation caching:

```text
COMPILATION_CACHE_ENABLE_CACHING = NO;
```

Change to:

```text
COMPILATION_CACHE_ENABLE_CACHING = YES;
```

Eager linking in Debug:

```text
EAGER_LINKING = YES;
```

Best-practice settings to generally keep once applied:

- `COMPILATION_CACHE_ENABLE_CACHING = YES`.
- `EAGER_LINKING = YES` for Debug.
- `SWIFT_USE_INTEGRATED_DRIVER = YES`.
- `DEBUG_INFORMATION_FORMAT = dwarf` for Debug.
- `SWIFT_COMPILATION_MODE = singlefile` for Debug.
- `ONLY_ACTIVE_ARCH = YES` for Debug.

## Script Phases

Release-only script guard:

```bash
[[ "$CONFIGURATION" != "Release" ]] && exit 0
./scripts/upload-dsyms.sh
```

Simulator guard:

```bash
[[ "$EFFECTIVE_PLATFORM_NAME" == "-iphonesimulator" ]] && exit 0
```

Add input/output files or `.xcfilelist` files for generators, linters and uploaders so Xcode can skip unchanged work. Do not add fake outputs just to silence warnings; outputs must represent actual produced files or stable stamp files.

## Source Compile Fixes

Complex chain:

```swift
let result = items.map { $0.value }.filter { $0 > threshold }.reduce(0, +)
```

Prefer:

```swift
let values: [Double] = items.map { $0.value }
let filteredValues: [Double] = values.filter { $0 > threshold }
let result: Double = filteredValues.reduce(0, +)
```

Complex nested expression:

```swift
let config = try JSONDecoder().decode(AppConfig.self, from: Data(contentsOf: url))
```

Prefer:

```swift
let configData: Data = try Data(contentsOf: url)
let config: AppConfig = try JSONDecoder().decode(AppConfig.self, from: configData)
```

Mark class `final` only after proving it is not subclassed:

```swift
final class NetworkService {
    func fetchData() async throws -> Data {
        try await client.data()
    }
}
```

Tighten access control only after searching usages:

```swift
private var internalState: State = .idle
private func processQueue() { }
```

Closure return type:

```swift
let handler: (Input) -> Output? = { (value: Input) -> Output? in
    guard let result = try? process(value) else { return nil }
    return result.transformed()
}
```

## SwiftUI

Extract large result-builder bodies into dedicated view structs. Prefer separate `struct View` types over many `@ViewBuilder` computed properties when type-checking is expensive.

Before:

```swift
struct ContentView: View {
    var body: some View {
        VStack {
            HeaderView(user: user)
            List(items) { item in
                HStack {
                    Text(item.title)
                    Spacer()
                    Text(item.subtitle)
                }
            }
        }
    }
}
```

After:

```swift
struct ContentView: View {
    var body: some View {
        VStack {
            HeaderView(user: user)
            ItemListView(items: items)
        }
    }
}

struct ItemListView: View {
    let items: [Item]

    var body: some View {
        List(items) { item in
            ItemRowView(item: item)
        }
    }
}
```

## SPM

Feature-to-feature cycle:

```swift
.target(name: "FeatureA", dependencies: ["FeatureB"]),
.target(name: "FeatureB", dependencies: ["FeatureA"]),
```

Prefer shared contracts:

```swift
.target(name: "SharedContracts", dependencies: []),
.target(name: "FeatureA", dependencies: ["SharedContracts"]),
.target(name: "FeatureB", dependencies: ["SharedContracts"]),
```

Interface/implementation split:

```swift
.target(name: "NetworkingInterface", dependencies: []),
.target(name: "Networking", dependencies: ["NetworkingInterface", "Models"]),
.target(name: "FeatureA", dependencies: ["NetworkingInterface"]),
```

Pin branch dependencies only after verifying available tags or choosing an explicit revision hash. Always run package resolution and a build after manifest changes.

## Regression Handling

Separate best-practice settings from speculative changes.

- Keep best-practice settings unless they break the build or the user rejects them.
- Revert speculative source, script or package changes when all relevant medians regress and no non-performance reason justifies keeping them.
- If only a cold clean build regresses but cached clean or incremental improves, present the tradeoff instead of automatically reverting.
