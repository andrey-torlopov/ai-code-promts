# Mode: registry

Use for creating or updating an AI setup registry from files that exist on disk.

## References

- `../references/registry-scan-scope.md`
- `../references/registry-schema.md`

## Workflow

1. Scan the root for anchors, workflow skills, knowledge packs and support files.
2. Count lines for each Markdown file.
3. Create or update the registry based only on existing files.
4. Add a changelog entry with an absolute date.
5. Verify paths in the registry exist.

## Stop

Do not invent missing files or future planned skills.
