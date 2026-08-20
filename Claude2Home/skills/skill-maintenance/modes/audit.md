# Mode: audit

Use for auditing AI instruction files, skills, stale references and non-atomic dependencies.

## References

- `../references/skill-audit-rules.md`
- `../references/stale-reference-signatures.md`
- `../references/skill-contract.md`
- `../scripts/skill-lint.sh`

## Workflow

1. Inventory `SKILL.md`, references, scripts, assets, runtime anchors and support files.
2. Verify frontmatter contains only `name` and `description`.
3. Check required references are local to the same skill folder or approved core/knowledge paths.
4. Check line counts, broken relative links, stale legacy references and unsupported metadata.
5. Save or return findings by severity.

## Stop

Do not edit files during audit unless the user asks for fixes.
