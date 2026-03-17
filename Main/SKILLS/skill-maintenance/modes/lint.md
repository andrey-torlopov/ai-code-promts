# Mode: lint

Use for fast validation or fixing documentation/instruction lint issues.

## References

- `../references/doc-review-phases.md`
- `../references/doc-check-rules.md`
- `../references/documentation-practices.md`
- `../references/skill-contract.md`
- `../scripts/skill-lint.sh`

## Workflow

1. Inventory requested Markdown and instruction files.
2. Apply size, structure, duplicate-content and link checks.
3. Run `scripts/skill-lint.sh` when the scope includes skills.
4. Apply safe fixes only when requested.
5. Report remaining findings.

## Stop

Do not audit source-code behavior.
