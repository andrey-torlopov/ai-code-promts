# Mode: scout

Use for first-entry repository inventory and onboarding maps.

## Knowledge

Per the scope table in `../SKILL.md`; no mode-specific additions.

## References

- `../references/ios-detection-patterns.md` - only when Apple-platform signals are present
- `../references/repo-scout-report-template.md`
- `../references/evidence-rules.md`

## Workflow

1. Detect build system and project signals.
2. Inventory source, test, docs, CI, linting, formatting and AI context files.
3. Catalog dependencies from package manager files.
4. Identify architecture, UI framework, storage, networking, concurrency and dependency injection signals.
5. Save or return the inventory report.

## Stop

Do not perform code review or dependency freshness checks unless the user explicitly requested that mode.
