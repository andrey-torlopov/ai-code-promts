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

- The selected skill can read `~/.claude/custom/CORE.md`, `~/.claude/custom/RESOLVER.md`, `~/.claude/custom/_core/`, its own folder and selected `~/.claude/custom/KNOWLEDGE/` packs.
- The selected skill must not require sibling skill folders.
- Cross-skill mentions are allowed only as routing notes or follow-up suggestions.
- Domain-specific rules belong in `~/.claude/custom/KNOWLEDGE/`, not in new top-level skills.
- A skill that changes files must own the reading required for those changes; do not design
  a skill that assumes another skill's reads.
