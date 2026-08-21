# Standalone Skill Template

Use this structure:

```markdown
---
name: concise-kebab-name
description: Action, target domain and trigger context.
---

# Human Readable Title

Read this file first. This skill is atomic and does not require sibling skill folders.

## Inputs

- Required input.
- Optional input.

## Workflow

1. Read the needed local references.
2. Inspect the real artifact or path.
3. Execute the task.
4. Verify the result.

## Local References

- `references/file.md` - when to read it.

## Output

Describe the exact artifact or response.

## Stop Conditions

- Conditions that require user input.
- Conditions that must not be handled by this skill.
```

Resource rules:

- `references/` stores Markdown checklists, policies, templates and examples loaded only when needed.
- `scripts/` stores executable utilities. Test scripts after adding them.
- `assets/` stores output templates or files used to produce artifacts.
- Do not add `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md` or extra documentation.
