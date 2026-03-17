# Mode: architecture

Use for onboarding-grade architecture documentation from real project files.

## Knowledge

Load by scope:

- Swift package or app code: `../../../KNOWLEDGE/swift/_rules.md`
- iOS/macOS app module: `../../../KNOWLEDGE/ios/_rules.md`
- CI/deployment architecture: `../../../KNOWLEDGE/devops/_rules.md`

## References

- `../references/module-analysis-checklist.md`
- `../references/module-architecture-doc-format.md`
- `../references/architecture-report-format.md`
- `../references/evidence-rules.md`

## Workflow

1. Verify scope exists.
2. Read complete relevant files for entry points, modules, types and data flow.
3. Document dependencies, boundaries, lifecycle and interactions.
4. Add recommendations only when supported by file evidence.
5. Save the document if an output path is provided.

## Stop

Deliver the architecture document. Do not modify code.
