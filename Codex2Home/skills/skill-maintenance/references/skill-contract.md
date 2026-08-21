# Skill Contract

## Required Structure

Every active `SKILL.md` must include:

1. YAML frontmatter with only `name` and `description`.
2. Purpose statement.
3. `SKILL CONTEXT` requirement.
4. Inputs.
5. Workflow.
6. Local References, Scripts or Assets when applicable.
7. Output.
8. Stop Conditions.

## Atomicity

- The selected skill can read `$CODEX_HOME/custom/CORE.md`, `$CODEX_HOME/custom/RESOLVER.md`, `$CODEX_HOME/custom/_core/`, its own folder and selected `$CODEX_HOME/custom/KNOWLEDGE/` packs.
- The selected skill must not require sibling skill folders.
- Cross-skill mentions are allowed only as routing notes or follow-up suggestions.
- Domain-specific rules belong in `$CODEX_HOME/custom/KNOWLEDGE/`, not in new top-level skills.
