# Dependency Check Report Format

```markdown
# Dependency Check Report

## Scope

## Package Managers

## Summary

| Metric | Value |
|---|---:|
| Total dependencies | count |
| SwiftPM dependencies | count |
| CocoaPods dependencies | count |
| Carthage dependencies | count |
| High risk constraints | count |

## Inventory

| Dependency | Manager | Constraint | Resolved | Targets | Category | Risk |
|---|---|---|---|---|---|---|

## Findings

| Severity | Dependency | Evidence | Recommendation |
|---|---|---|---|

## Update Notes

## Verification
```

Adapt manager-specific rows (SwiftPM/CocoaPods/Carthage) to the package managers actually
detected in the project.
