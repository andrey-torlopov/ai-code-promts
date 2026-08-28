# Mode: architecture

Use for onboarding-grade architecture documentation from real project files.

## Knowledge

Load by scope:

- Swift package or app code: `$CODEX_HOME/custom/KNOWLEDGE/swift/_rules.md`
- iOS/macOS app module: `$CODEX_HOME/custom/KNOWLEDGE/ios/_rules.md`
- CI/deployment architecture: `$CODEX_HOME/custom/KNOWLEDGE/devops/_rules.md`
- No matching domain pack: `$CODEX_HOME/custom/KNOWLEDGE/general/_rules.md`

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
