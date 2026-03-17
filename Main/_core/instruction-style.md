# Instruction Style

Keep instruction files compact and operational.

## Rules

1. Put global invariants in `CORE.md`.
2. Put routing decisions in `RESOLVER.md`.
3. Put workflow details in one selected skill.
4. Put domain rules in `KNOWLEDGE/`.
5. Do not duplicate long policies across anchors, skills and references.
6. Do not require sibling skill folders for the selected skill's core deliverable.
7. Prefer concrete gates, inputs, outputs and stop conditions over persona text.

## Entry Points

Runtime anchors are thin:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`

They point to `CORE.md` and `RESOLVER.md`; they do not own rules.
