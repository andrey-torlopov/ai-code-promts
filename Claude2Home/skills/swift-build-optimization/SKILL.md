---
name: swift-build-optimization
description: Benchmarks, analyzes, plans and applies approved Xcode, Swift, iOS and macOS build-time optimizations. Use when a developer asks to speed up clean or incremental Xcode builds, reduce iOS build time, investigate Swift compile hotspots, audit Xcode build settings, diagnose SPM build overhead, or verify before/after build performance.
---

# Swift Build Optimization

Skill root: `~/.claude/skills/swift-build-optimization/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

Read this file first. This skill is atomic and does not require sibling skill folders.

Use this skill for evidence-backed Xcode build optimization. Wall-clock build time is the primary metric: how long the developer actually waits for a clean, cached clean, zero-change or touched-file incremental build.

## SKILL CONTEXT

Before substantial work, output the block from `~/.claude/custom/_core/skill-context.md`.
Set `mode` to one of:

- `benchmark`
- `analyze`
- `fix`
- `verify`

Load `~/.claude/custom/KNOWLEDGE/swift` and `~/.claude/custom/KNOWLEDGE/ios` for Xcode, Swift, iOS, macOS, `.xcodeproj`, `.xcworkspace`, `Package.swift` or `Package.resolved` work. Skip unrelated knowledge packs unless the project scope requires them.

## Inputs

- Project root.
- `.xcodeproj` or `.xcworkspace` path.
- Scheme, configuration and destination.
- Pain point: clean build, cached clean build, zero-change incremental, touched-file incremental, CI build, package resolution or compile hotspots.
- Existing benchmark artifact or raw `xcodebuild -showBuildTimingSummary` output when available.
- Optional representative Swift file to touch for real incremental benchmarking.
- Optional approved plan at `.build-benchmark/optimization-plan.md`.

## Workflow

1. Classify the request as benchmark-only, analyze/recommend, approved fix, or verify.
2. Read only the local references required for that class of work.
3. Resolve bundled scripts relative to this `SKILL.md`; do not assume the target repository has a `scripts/` directory.
4. Measure before recommending changes unless a fresh, comparable `.build-benchmark/*.json` artifact already exists.
5. Preserve raw build logs and JSON artifacts under `.build-benchmark/`.
6. Compare wall-clock medians first. Treat timing-summary category totals as diagnostic evidence, not as developer wait time.
7. Produce a prioritized plan with an approval checklist before changing project files, source files, package manifests, schemes or scripts.
8. Apply only explicitly approved items, one logical fix at a time.
9. Rebuild and re-benchmark with the same inputs after approved changes.
10. Report the wall-clock delta with numerator and denominator for every percentage.

## Local References

- `references/workflow.md` - read for the detailed benchmark/analyze/fix/verify sequence and script invocation rules.
- `references/audit-checks.md` - read when auditing project settings, run scripts, compile hotspots, SPM graph, macros, assets or CocoaPods usage.
- `references/build-settings-best-practices.md` - read for Debug, Release and cross-target build setting expectations.
- `references/recommendation-format.md` - read before writing `.build-benchmark/optimization-plan.md` or an execution report.
- `references/fix-patterns.md` - read before applying approved source, build setting, script phase or SPM fixes.
- `references/source-attribution.md` - read when modifying bundled scripts or copying this skill.

## Scripts And Schemas

- `scripts/benchmark_builds.py` - repeatable clean, cached clean, zero-change and touched-file incremental benchmarks.
- `scripts/diagnose_compilation.py` - Swift frontend type-checking and optional per-file diagnostics.
- `scripts/generate_optimization_report.py` - Markdown report and approval checklist generator from benchmark and diagnostics artifacts.
- `scripts/check_spm_pins.py` - branch-pinned SPM dependency scan.
- `scripts/summarize_build_timing.py` - parse Build Timing Summary output from a log.
- `scripts/render_recommendations.py` - render JSON recommendations to Markdown.
- `schemas/build-benchmark.schema.json` - benchmark artifact schema.

## Output

Depending on mode, return one of:

- Benchmark summary with clean, cached clean, zero-change and touched-file incremental medians/min/max, top timing categories, variance notes and artifact paths.
- Recommendation plan at `.build-benchmark/optimization-plan.md` with evidence, wait-time impact, actionability, risk and approval checklist.
- Execution report with files changed, post-change benchmark medians, absolute deltas and percentage deltas.
- Blocker report when the project cannot build or the requested optimization lacks measurable evidence.

Percentage formula:

```text
percent faster = ((baseline_median_seconds - post_change_median_seconds) / baseline_median_seconds) * 100
```

Show the substituted numerator and denominator in user-facing reports.

Every substantial run ends with the final `TRACE` block from `~/.claude/custom/RESOLVER.md`, reporting references read, knowledge read, patterns or policies applied, verification and residual risk.

## Stop Conditions

- Stop before modifying `.xcodeproj`, `.xcworkspace`, schemes, `Package.swift`, source files, run scripts or CI files unless the developer explicitly approved the exact change.
- Stop if no buildable baseline exists; report the failing command and logs needed to make the project buildable first.
- Do not present cumulative task seconds as wall-clock savings.
- Do not audit or mutate `Pods.xcodeproj` or Podfile-specific CocoaPods settings; recommend migration to SPM when CocoaPods is the bottleneck.
- Do not change third-party dependency source code unless the user explicitly scoped that dependency as editable.
- Do not require or read sibling skill folders.
