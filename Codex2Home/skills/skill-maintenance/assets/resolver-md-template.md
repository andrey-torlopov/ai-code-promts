# Skill Resolver

> Standalone fallback. Use only for a repository that must work without
> the global router in `$CODEX_HOME/custom/RESOLVER.md`.

Use the first concrete deliverable match.

| Request signal | Skill | Deliverable |
|---|---|---|
| analyze, plan, review, research, spec | `analysis-plan` | Report, findings or plan |
| implement, fix, edit | `implementation-from-plan` | Changed files plus verification |
| build/CI/runtime failure | `debug-diagnose` | Root cause plus fix plan |
| local shell/filesystem task | `mac-local-ops` | Safe local action/report |
| deploy/release/publish/rollout | `deploy-ops` | Gated operation |
| instruction/skill maintenance | `skill-maintenance` | Changed skills or audit |
