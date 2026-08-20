# Stale Reference Signatures

Search for these strings:

```text
allowed-tools:
context:
agents/openai.yaml
_ai/layers/
_ai/skills/
writing-plans
dev_agent.md
qa_agent.md
agents/sdet.md
agents/auditor.md
Protocol Injection
Escalation Protocol
gardener.md
```

Interpretation:

- In migrated standalone skills, required references to `_ai/` are stale.
- In migration reports, `_ai/` may be valid historical context.
- `writing-plans` is stale unless a local implementation-planning skill exists in the same skill folder.
