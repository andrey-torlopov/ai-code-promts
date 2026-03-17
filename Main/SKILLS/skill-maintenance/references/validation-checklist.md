# Validation Checklist

Check every new or edited skill:

- Folder name equals YAML `name`.
- Folder name is kebab-case lowercase.
- `SKILL.md` exists and starts with YAML frontmatter.
- Frontmatter contains only `name` and `description`.
- No `agents/openai.yaml` exists.
- Required local references exist.
- Required scripts exist and are executable when they are shell scripts.
- `SKILL.md` can be used without reading sibling skill folders.
- Required workflow has inputs, steps, output and stop conditions.
- No unresolved `TODO`, `TBD` or placeholder text in operational instructions.
- No stale required references to `_ai/` paths.
- `SKILL.md` is compact enough to load directly.

Formula for completion reporting:

```text
passed checks / total checks = actual_passed / actual_total
```
