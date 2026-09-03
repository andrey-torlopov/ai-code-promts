# Mode: deps

Use for dependency inventory, version constraints, duplication, compatibility and update risk.

## Knowledge

Per the scope table in `../SKILL.md`; no mode-specific additions.

## References

- `../references/dependency-categories.md`
- `../references/dependency-version-risk-model.md`
- `../references/dependency-report-format.md`

## Workflow

1. Locate dependency manager files.
2. Inventory dependency names, constraints, resolved versions and target usage when available.
3. Classify dependencies by category.
4. Detect strict pins, branch dependencies, revision dependencies, duplicate managers and platform concerns.
5. In `online-latest` mode, verify latest versions from current primary sources before recommending updates.

## Stop

If no dependency manager files exist, report checked paths. Do not review source behavior.
