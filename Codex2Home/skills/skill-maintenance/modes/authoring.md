# Mode: authoring

Use for creating or updating Markdown-only skill folders.

## References

- `../references/yaml-reference.md`
- `../references/skill-template.md`
- `../references/validation-checklist.md`
- `../references/interaction-guide.md`
- `../references/skill-contract.md`
- `../scripts/init_skill.sh`

## Workflow

1. Clarify purpose, triggers, inputs, outputs and stop conditions.
2. Decide whether this should be a new top-level workflow skill, a mode or a knowledge pack.
3. Create `SKILL.md` with only `name` and `description` in YAML frontmatter.
4. Add only necessary local references, scripts and assets.
5. Validate atomicity and local references.

## Stop

Return created/changed paths and validation status.
