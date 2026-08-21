# YAML Frontmatter Reference

Every `SKILL.md` must start with:

```yaml
---
name: skill-name
description: What the skill does and when to use it.
---
```

Rules:

- `name` is required.
- `name` must match the folder name.
- `name` uses lowercase letters, digits and hyphens only.
- `description` is required.
- `description` must include both capability and trigger context.
- Do not add `allowed-tools`, `context`, `agent`, metadata, tags or UI fields.
- Do not create `agents/openai.yaml` for this repository.

Good descriptions:

- `Reviews Swift code, modules, pull requests and diffs for correctness, crashes, retain cycles and concurrency issues. Use for Swift review requests.`
- `Creates standalone Markdown-only skill folders. Use when designing, scaffolding or validating local SKILLS packages.`

Bad descriptions:

- `Helps with code.`
- `This skill is designed to maybe assist with things.`
- `Swift.`
