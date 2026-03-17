# Mode: ai-context-init

Use for generating compact AI context files for a project.

## References

- `../assets/core-md-template.md`
- `../assets/resolver-md-template.md`
- `../assets/agents-md-template.md`
- `../assets/claude-md-template.md`
- `../assets/gemini-md-template.md`

## Workflow

1. Inspect the target project for language, build system, dependencies, tests, linting and CI.
2. If existing `CORE.md`, `RESOLVER.md`, `COMMON.md`, `AGENTS.md`, `CLAUDE.md` or `GEMINI.md` files exist, stop and ask before overwrite.
3. Generate compact project-specific files from local assets.
4. Do not invent CI, architecture or commands that are not verified.
5. Validate anchors stay short and point to `CORE.md` and `RESOLVER.md`.

## Stop

Do not overwrite existing context files without explicit confirmation.
