# Mode: ai-context-init

Use for generating compact AI context files for a project.

The global system in `$CODEX_HOME/custom/` is already loaded in every session.
A project therefore gets a thin anchor plus verified facts, not a second copy of the rules.

## References

- `../assets/agents-md-template.md`
- `../assets/project-facts-template.md`
- Optional non-Codex anchors: `../assets/claude-md-template.md`, `../assets/gemini-md-template.md`
- Standalone fallback only: `../assets/core-md-template.md`, `../assets/resolver-md-template.md`, `../assets/common-md-template.md`

## Workflow

1. Detect whether the global system exists: `$CODEX_HOME/custom/CORE.md` and `$CODEX_HOME/custom/RESOLVER.md`.
2. Inspect the target project for language, build system, dependencies, tests, linting and CI.
3. If `AGENTS.override.md`, `AGENTS.md` or `PROJECT.md` already exists in the project,
   stop and ask before overwrite.
4. Global system present: generate a thin Codex `AGENTS.md` anchor from
   `agents-md-template.md` plus `PROJECT.md` from `project-facts-template.md`.
5. Global system absent: generate the standalone set from the fallback assets.
6. Do not invent CI, architecture or commands that are not verified against the repository.
7. Keep the Codex anchor short and pointing at `$CODEX_HOME/custom/CORE.md` and
   `$CODEX_HOME/custom/RESOLVER.md`. Generate Claude or Gemini anchors only when the
   user explicitly requests those runtimes and their global-home contract is known.
8. Never write into `$CODEX_HOME/` from this mode; it produces project files only.

## Naming

The facts file is `PROJECT.md` in the repository root.
Use `.claude/PROJECT.md` only when a `PROJECT.md` already exists there for another purpose.
Do not invent alternative names; the global system reads only these two paths.

## Stop

Do not overwrite existing context files without explicit confirmation.
Do not modify the global system here; that is the `authoring` and `audit` modes' scope.
