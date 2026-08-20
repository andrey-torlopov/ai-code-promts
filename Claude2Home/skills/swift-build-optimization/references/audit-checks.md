# Audit Checks

Use this reference to decide what to inspect after benchmarking.

## Project And Scheme

- Target dependencies are explicit and accurate.
- Scheme builds targets in dependency order, not accidental manual order.
- Monolithic targets are not serializing work that could be split safely.
- `DEFINES_MODULE` is enabled where custom frameworks should benefit from module maps.
- Public headers are self-contained and use framework-qualified imports where module maps exist.
- Explicit module settings are consistent across targets that should share built modules.

## Run Script Phases

- Scripts declare input and output files.
- Long input/output lists use `.xcfilelist`.
- Release-only scripts are skipped in Debug.
- Device-only or upload scripts are skipped for simulator builds.
- Scripts avoid touching file timestamps unless content changes.
- `alwaysOutOfDate = 1` is justified by real behavior.
- Scripts with declared dependencies can run in parallel instead of blocking compilation.

High-impact script symptoms:

- `PhaseScriptExecution` dominates zero-change builds.
- No-op rebuilds still run linters, generators, uploaders or formatters.
- `Planning Swift module` is large while no compiles are scheduled.

## Zero-Change Overhead

Investigate fixed-cost categories when an immediate no-edit rebuild exceeds a few seconds:

- `PhaseScriptExecution`.
- `CodeSign`.
- `ValidateEmbeddedBinary`.
- `CopySwiftLibs`.
- `RegisterWithLaunchServices`.
- `ProcessInfoPlistFile`.
- `ExtractAppIntentsMetadata`.

Classify `ExtractAppIntentsMetadata` as `xcode-behavior` unless there is a clear repo-local Apple-supported control.

## Asset Catalogs

- `CompileAssetCatalog` is single-threaded per target.
- Multiple catalogs in the same target compile sequentially.
- Asset catalog compilation is not served by the Xcode compilation cache.
- If this category blocks wall-clock time, consider separate resource-bundle targets so catalogs can compile in parallel.

## Build Settings

Read `build-settings-best-practices.md` and audit Debug, Release and cross-target consistency. Do not flag language migration settings such as `SWIFT_STRICT_CONCURRENCY` or `SWIFT_UPCOMING_FEATURE_*` as build-time issues.

## Compile Hotspots

Use compile diagnostics when timing evidence points to Swift or mixed-language compilation.

Inspect:

- `SwiftCompile`, `CompileSwiftSources`, `SwiftEmitModule`, `CompileC` and `Planning Swift module`.
- `-warn-long-function-bodies`.
- `-warn-long-expression-type-checking`.
- Optional `-debug-time-compilation`, `-debug-time-function-bodies`, `-driver-time-compilation` and `-stats-output-dir`.

Code patterns to check:

- Complex inferred expressions without intermediate typed variables.
- Long generic chains such as `map`/`flatMap`/`filter`/`reduce`.
- Nested ternaries or overloaded generic calls.
- SwiftUI `body` values over roughly 50 lines or deeply nested result builders.
- `@ViewBuilder` helper properties that should be separate `struct View` types.
- Closures passed to generic APIs without explicit parameter or return types.
- Delegates typed as `AnyObject` instead of a concrete protocol.
- Broad Objective-C bridging headers and generated Swift-to-Objective-C surfaces.
- Classes not marked `final` when never subclassed.
- `public` or `open` symbols that are only used internally.

If compile categories are mostly parallel work, label findings as compiler workload reductions rather than wait-time reductions.

## SPM Graph

Inspect `Package.swift`, `Package.resolved`, project package references and build logs.

Checks:

- Local packages are actually referenced by `XCLocalSwiftPackageReference`.
- Remote package products are actually linked via `XCSwiftPackageProductDependency`.
- Branch-pinned dependencies are justified or can be pinned to tags/revisions.
- Build-tool plugins do not run on every incremental build without input changes.
- Large umbrella packages do not trigger broad rebuilds.
- Dependencies flow in one direction: Common/Core -> Services/Domain -> Features/UI.
- Feature modules do not depend on each other directly.
- Shared contracts are extracted to lower-layer modules.
- Target-level cycles are removed; SPM package cycles do not make target cycles acceptable.
- Oversized modules, roughly 200+ files, are split only when benchmark evidence supports it.
- `@_exported import` is not creating hidden rebuild chains.
- Test targets depend on the module under test, not the whole app target.

## Swift Macros

- Heavy macro usage can cause near-full incremental rebuilds after trivial changes.
- `swift-syntax` may build for multiple architectures when no prebuilt binary is available.
- Isolate macro-heavy code in fewer, stable modules when it reduces invalidation scope.

## Multi-Platform Multiplication

Projects with iOS plus watchOS, Catalyst or macOS targets may build shared packages for multiple platform/architecture slices. Check for duplicate `SwiftCompile`, `SwiftEmitModule` and `ScanDependencies` tasks before recommending graph changes.

## CocoaPods

When `Podfile`, `Pods/` or `Pods.xcodeproj` exists:

- Do not tune `Pods.xcodeproj`.
- Do not recommend CocoaPods-specific linkage or code-sign tweaks as build optimizations.
- Recommend migration to SPM as a long-term option when package manager overhead is material.
- Continue auditing first-party targets and build settings the project controls.

## Priority Model

High:

- Serial critical-path script or asset bottlenecks.
- Missing script metadata causing every incremental build to do work.
- Configuration drift causing duplicate module variants.
- Large `Planning Swift module` due to input invalidation.
- Macro or package graph cascading that causes near-full rebuilds.

Medium:

- Slow asset catalog compilation that may be parallelized.
- Oversized modules with measurable incremental pain.
- Package plugins adding fixed overhead.
- Cross-target settings cleanup with plausible module reuse impact.

Low:

- Cosmetic build setting cleanup without current evidence.
- Isolated type-check warnings outside hot modules.
- CI-only checkout cost when the user cares about local edit-loop time.
