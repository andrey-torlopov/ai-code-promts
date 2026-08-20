# Mode: spec

Use for product, feature or implementation ideas that need requirements, trade-offs and design approval.

## Knowledge

Load domain packs only after inspecting the project context and confirming the affected stack.

## References

- `../references/spec-reviewer-prompt.md`
- `../references/visual-companion.md`
- `../references/evidence-rules.md`

## Workflow

1. Inspect current project context.
2. Ask clarifying questions one at a time when requirements are ambiguous.
3. If the idea contains independent subsystems, decompose it and pick the first bounded spec.
4. Propose two or three approaches with trade-offs and a recommendation.
5. Present architecture, components, data flow, error handling and verification.
6. Get explicit approval when the spec is meant to guide implementation.
7. Write the design spec to the requested path or a clear docs path.
8. Review the spec using `../references/spec-reviewer-prompt.md`.

## Stop

Do not write production code, scaffold a project or commit files.
