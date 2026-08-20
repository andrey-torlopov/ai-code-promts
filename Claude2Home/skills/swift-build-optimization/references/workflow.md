# Workflow

Use this reference for the operational sequence. Keep analysis and mutation separated.

## Script Path Rule

Resolve scripts from the skill directory, not from the project root.

```bash
SKILL_DIR="$(pwd)"
python3 "$SKILL_DIR/scripts/benchmark_builds.py" --help
```

Run that command only after changing into the directory that contains this `SKILL.md`, or set `SKILL_DIR` programmatically to that directory from the agent runtime.

## Phase 0: Context

Collect or infer:

- `.xcodeproj` or `.xcworkspace`.
- Scheme.
- Configuration, usually `Debug` for local iteration.
- Destination, for example iOS Simulator or macOS.
- Whether the user cares about clean, cached clean, zero-change incremental, touched-file incremental, CI, SPM resolve time or compile diagnostics.
- Xcode version from `xcodebuild -version`.
- Dirty worktree status before edits.

When both `.xcworkspace` and `.xcodeproj` exist, prefer the project only if it can build independently. Use the workspace when it contains required subprojects or package integration.

## Phase 1: Benchmark

Run a repeatable baseline unless a fresh comparable artifact already exists.

```bash
python3 "$SKILL_DIR/scripts/benchmark_builds.py" \
  --project "$PROJECT_PATH" \
  --scheme "$SCHEME" \
  --configuration "$CONFIGURATION" \
  --destination "$DESTINATION" \
  --output-dir .build-benchmark
```

Use `--workspace "$WORKSPACE_PATH"` instead of `--project "$PROJECT_PATH"` for workspace builds.

For true edit-loop measurement, add:

```bash
--touch-file "$REPRESENTATIVE_SWIFT_FILE"
```

The benchmark script:

- runs clean builds;
- auto-detects `COMPILATION_CACHE_ENABLE_CACHING = YES`;
- adds cached clean builds when caching is enabled;
- runs zero-change incremental builds by default;
- writes raw logs and a JSON artifact to `.build-benchmark/`.

If an SPM package has `exclude:` paths pointing to gitignored directories, create the missing directories before resolving packages. Worktrees often omit gitignored folders that package manifests still reference.

## Phase 2: Confidence Check

For each measured build type, compute:

```text
variance_ratio = (max_seconds - min_seconds) / median_seconds
```

Example:

```text
variance_ratio = (74.2 - 60.0) / 68.0 = 14.2 / 68.0 = 20.9%
```

If the ratio is above `20%`, label the benchmark high variance and avoid strong claims unless the post-change median falls outside the baseline min/max range.

## Phase 3: Analyze

Read `audit-checks.md` and the relevant domain sections.

Prioritize by likely wall-clock impact:

1. Serial bottlenecks on the critical path, such as `PhaseScriptExecution`, `CompileAssetCatalog`, `CodeSign` or validation.
2. Incremental invalidation issues such as large `Planning Swift module`, repeated `SwiftEmitModule` or scripts touching timestamps.
3. Build setting mismatches and target-level drift that create module variants.
4. Compile hotspots only when compile work appears to block wall-clock progress.
5. Package graph, plugin and macro cascading issues.

If the sum of timing-summary category seconds is at least `2 * wall_clock_median`, most work is parallelized. In that case, compile hotspot fixes may reduce CPU work without reducing wait time. Say that plainly.

## Phase 4: Compilation Diagnostics

Run diagnostics when `SwiftCompile`, `SwiftEmitModule`, `Planning Swift module` or type-check warnings are important evidence.

```bash
python3 "$SKILL_DIR/scripts/diagnose_compilation.py" \
  --project "$PROJECT_PATH" \
  --scheme "$SCHEME" \
  --configuration "$CONFIGURATION" \
  --destination "$DESTINATION" \
  --threshold 100 \
  --output-dir .build-benchmark
```

Use `--per-file-timing` for file ranking and `--stats-output` only when the extra output is worth the build cost.

## Phase 5: SPM Pin Scan

When branch-pinned SPM dependencies are suspected:

```bash
python3 "$SKILL_DIR/scripts/check_spm_pins.py" --project "$PROJECT_PATH"
```

This may require network access because it checks remote tags. If tags do not exist, recommend pinning to a revision hash for determinism rather than inventing a semver target.

## Phase 6: Optimization Plan

Generate or manually write `.build-benchmark/optimization-plan.md`.

```bash
python3 "$SKILL_DIR/scripts/generate_optimization_report.py" \
  --benchmark "$BENCHMARK_JSON" \
  --project-path "$PROJECT_PATH" \
  --diagnostics "$DIAGNOSTICS_JSON" \
  --output .build-benchmark/optimization-plan.md
```

If additional findings were produced manually, add them using the structure in `recommendation-format.md`.

Stop after the plan unless the user explicitly approves changes.

## Phase 7: Approved Fixes

Before editing, read `fix-patterns.md`.

Implementation rules:

- Implement only checked or explicitly named items.
- Keep one logical change per edit group.
- Verify with `xcodebuild build` after changes.
- Re-benchmark with the same project, scheme, configuration, destination and repeats.
- If a speculative change regresses all relevant medians, recommend reverting it.
- Keep low-risk best-practice build settings once applied even if one noisy benchmark shows no immediate improvement; report them as best-practice alignment, not measured wins.

## Phase 8: Final Report

Lead with wall-clock results:

```text
Incremental build now takes 8.4s, was 12.1s: 3.7s faster.
percent faster = ((12.1 - 8.4) / 12.1) * 100 = 3.7 / 12.1 * 100 = 30.6%
```

Then include:

- artifacts read and written;
- changes applied;
- unchanged approved items and why;
- benchmark variance;
- residual risks and follow-up opportunities.
