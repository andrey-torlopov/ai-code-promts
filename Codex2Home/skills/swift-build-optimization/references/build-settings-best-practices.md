# Build Settings Best Practices

Scope: build performance only. Do not flag language migration choices as performance issues.

Report settings as:

```markdown
- [x] `KEY`: `actual` (recommended: `expected`)
- [ ] `KEY`: `actual` (recommended: `expected`)
```

## Debug

| Setting | Key | Recommended | Risk | Why |
|---|---|---|---|---|
| Compilation mode | `SWIFT_COMPILATION_MODE` | `singlefile` or unset when Xcode defaults to incremental | Low | Recompiles changed files instead of the whole target. |
| Swift optimization | `SWIFT_OPTIMIZATION_LEVEL` | `-Onone` | Low | Avoids optimization passes in local builds. |
| C/ObjC optimization | `GCC_OPTIMIZATION_LEVEL` | `0` | Low | Avoids C-family optimization passes. |
| Active arch only | `ONLY_ACTIVE_ARCH` | `YES` | Low | Avoids building unused architectures locally. |
| Debug info | `DEBUG_INFORMATION_FORMAT` | `dwarf` | Low | Avoids separate dSYM generation during local debug builds. |
| Testability | `ENABLE_TESTABILITY` | `YES` | Low | Required for `@testable import`; expected debug overhead. |
| Debug condition | `SWIFT_ACTIVE_COMPILATION_CONDITIONS` | includes `DEBUG` | Low | Keeps debug-only code paths correct. |
| Eager linking | `EAGER_LINKING` | `YES` | Low | Lets linking overlap with compilation where supported. |

## Release

| Setting | Key | Recommended | Risk | Why |
|---|---|---|---|---|
| Compilation mode | `SWIFT_COMPILATION_MODE` | `wholemodule` | Low | Optimizes runtime binary output. |
| Swift optimization | `SWIFT_OPTIMIZATION_LEVEL` | `-O` or `-Osize` | Low | Produces optimized distribution builds. |
| C/ObjC optimization | `GCC_OPTIMIZATION_LEVEL` | `s` | Low | Optimizes C-family release output for size. |
| Active arch only | `ONLY_ACTIVE_ARCH` | `NO` | Low | Release builds must include distribution architectures. |
| Debug info | `DEBUG_INFORMATION_FORMAT` | `dwarf-with-dsym` | Low | Required for production crash symbolication. |
| Testability | `ENABLE_TESTABILITY` | `NO` | Low | Removes internal-symbol export overhead from release. |

## All Configurations

| Setting | Key | Recommended | Risk | Why |
|---|---|---|---|---|
| Compilation caching | `COMPILATION_CACHE_ENABLE_CACHING` | `YES` | Low | Reuses Swift and C-family compile outputs for repeated inputs. |
| Integrated Swift driver | `SWIFT_USE_INTEGRATED_DRIVER` | `YES` | Low | Avoids separate process scheduling overhead in migrated projects. |
| Clang modules | `CLANG_ENABLE_MODULES` | `YES` | Low | Reuses module maps instead of reparsing headers. |
| Explicit Swift modules | `SWIFT_ENABLE_EXPLICIT_MODULES` or `_EXPERIMENTAL_SWIFT_EXPLICIT_MODULES` | evaluate per project | Medium | Can improve scheduling and module visibility but may add scan overhead. Benchmark before and after. |

## Cross-Target Consistency

Prefer project-level settings unless a target has a clear reason to override.

Check drift in:

- `SWIFT_COMPILATION_MODE`.
- `SWIFT_OPTIMIZATION_LEVEL`.
- `ONLY_ACTIVE_ARCH`.
- `DEBUG_INFORMATION_FORMAT`.
- `OTHER_SWIFT_FLAGS`.
- Preprocessor macros that affect imported package modules.

Different settings across targets importing the same packages can create duplicate module variants and inflate `SwiftEmitModule` or scan tasks.

## Out Of Scope

Do not flag these as build-performance recommendations:

- `SWIFT_STRICT_CONCURRENCY`.
- `SWIFT_UPCOMING_FEATURE_*`.
- `SWIFT_APPROACHABLE_CONCURRENCY`.
- Non-`DEBUG` values in `SWIFT_ACTIVE_COMPILATION_CONDITIONS` when they are intentional app, widget or app-clip configuration.
