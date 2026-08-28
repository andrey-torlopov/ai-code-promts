# General Rules

Fallback pack for stacks and scopes with no dedicated `KNOWLEDGE/<domain>/` pack.
When a dedicated pack exists for the detected stack, load it instead and list this one under `SKIPPED`.

1. Detect the stack before acting: manifests, lockfiles, build files and CI config decide the tooling; never guess commands.
2. Follow the project's existing conventions for naming, formatting, layout and error handling over any external style guide.
3. Prefer the smallest idiomatic construct of the language at hand; do not import patterns from another ecosystem.
4. Do not add dependencies, tools or new top-level structure without an explicit request or confirmation.
5. Handle errors explicitly: no swallowed errors, no empty catch blocks, no silent fallback values on failure paths.
6. Keep behavior deterministic: no hidden network calls; no time-, locale- or randomness-dependent logic in tests.
7. Do not log or print secrets, tokens or personal data.
8. Use typed or structured representations for structured data instead of stringly-typed maps when the language offers them.
9. Tests must be isolated, order-independent and free of sleep-based synchronization.
10. Verification follows `verification.md`: a named command with observed output, or an explicit statement of what was not run and why.
