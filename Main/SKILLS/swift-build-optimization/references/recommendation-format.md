# Recommendation Format

Every recommendation must be evidence-backed and framed in wall-clock impact.

## Required Fields

- `title`.
- `wait_time_impact`.
- `actionability`.
- `category`.
- `observed_evidence`.
- `estimated_impact`.
- `confidence`.
- `approval_required`.
- `benchmark_verification_status`.
- `risk_level`.

## Actionability

- `repo-local` - fix is in project files, source, schemes or local scripts.
- `package-manager` - fix touches SPM/CocoaPods/dependency configuration and may have broad side effects.
- `xcode-behavior` - measured cost is driven by Xcode and has no safe repo-local fix.
- `upstream` - fix belongs in a third-party dependency or external tool.

## Impact Language

Use one of:

- `Expected to reduce clean build wait time by approximately X seconds.`
- `Expected to reduce incremental build wait time by approximately X seconds.`
- `Reduces parallel compile work but is unlikely to reduce build wait time because other tasks take equally long.`
- `Impact on wait time is uncertain; re-benchmark after applying to confirm.`
- `No wait-time improvement expected. The benefit is deterministic builds, faster branch switching or reduced CI cost.`

Do not headline cumulative task-time savings. If a change removes 5 seconds of parallel compile work but another 5-second serial task still blocks completion, the developer does not get a 5-second wait-time improvement.

## Approval Checklist

Plans must include:

```markdown
## Approval Checklist

- [ ] **1. Recommendation title** -- Impact: expected wait-time impact | Actionability: repo-local | Risk: Low
- [ ] **2. Recommendation title** -- Impact: uncertain, re-benchmark | Actionability: package-manager | Risk: Medium
```

Stop after presenting this list unless the user explicitly approves items.

## Delta Math

For every before/after metric:

```text
absolute_delta_seconds = baseline_median_seconds - post_change_median_seconds
percent_faster = ((baseline_median_seconds - post_change_median_seconds) / baseline_median_seconds) * 100
```

Example:

```text
absolute_delta_seconds = 18.6 - 12.4 = 6.2s
percent_faster = ((18.6 - 12.4) / 18.6) * 100 = 6.2 / 18.6 * 100 = 33.3%
```

If the post-change value is slower, state it as a regression:

```text
percent_slower = ((post_change_median_seconds - baseline_median_seconds) / baseline_median_seconds) * 100
```

## Optimization Plan Shape

```markdown
# Xcode Build Optimization Plan

## Project Context
- Project/workspace:
- Scheme:
- Configuration:
- Destination:
- Xcode:
- Benchmark artifact:

## Baseline Benchmarks

| Metric | Clean | Cached Clean | Zero-Change | Touched-File Incremental |
|---|---:|---:|---:|---:|
| Median | | | | |
| Min | | | | |
| Max | | | | |
| Runs | | | | |

## Timing Summary

State that category seconds are aggregated task time and may exceed wall-clock time because Xcode runs tasks in parallel.

## Build Settings Audit

Use `[x]` and `[ ]` rows from `build-settings-best-practices.md`.

## Compilation Diagnostics

Include top function/expression/file hotspots when diagnostics were run. State explicitly when skipped.

## Prioritized Recommendations

For each item: title, wait-time impact, actionability, evidence, estimated impact, confidence, risk and approval requirement.

## Approval Checklist

Unchecked boxes for user approval.
```

## Execution Report Shape

```markdown
## Execution Report

### Baseline
- Clean build median:
- Cached clean build median:
- Incremental build median:

### Changes Applied

| # | Change | Actionability | Measured Result | Status |
|---|---|---|---|---|
| 1 | | | | Kept / Kept (best practice) / Reverted / Blocked / No improvement |

### Final Cumulative Result
- Clean:
- Cached clean:
- Incremental:
- Net result:

### Blocked Or Non-Actionable Findings
- Finding:
```

## Verification Status

- `Not yet verified`.
- `Queued for verification`.
- `Verified improvement`.
- `No measurable improvement`.
- `Inconclusive due to benchmark noise`.
