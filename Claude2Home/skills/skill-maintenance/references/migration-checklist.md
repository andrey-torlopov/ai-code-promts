# Migration Checklist

Use before deleting old instruction surfaces:

1. New canonical route exists in `~/.claude/custom/RESOLVER.md`.
2. Useful workflow rules moved to an active workflow skill.
3. Domain-specific rules moved to `~/.claude/custom/KNOWLEDGE/`.
4. Runtime anchors point to `~/.claude/custom/CORE.md` and `~/.claude/custom/RESOLVER.md`.
5. Active references to old paths are removed.
6. Lint passes.
7. Regression prompts route correctly.

If the user explicitly permits removal and the repository has git history, old legacy files can be deleted after this checklist passes.
