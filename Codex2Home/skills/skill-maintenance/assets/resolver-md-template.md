# Skill Resolver

> Standalone fallback. Use only for a repository that must work without
> the global router in `$CODEX_HOME/custom/RESOLVER.md`.

Use the most specific matching row: a row that names the failure, domain or system beats a
generic analysis row.

| Request signal | Skill | Deliverable |
|---|---|---|
| Xcode/Swift build-time optimization | `swift-build-optimization` | Benchmarks, plan, approved fixes |
| build/CI/runtime/environment failure | `debug-diagnose` | Root cause plus fix plan |
| deploy/release/publish/rollout | `deploy-ops` | Gated operation |
| instruction/skill maintenance or audit | `skill-maintenance` | Changed skills or audit |
| analyze, plan, review, research, spec | `analysis-plan` | Report, findings or plan |
| implement, fix, edit | `implementation-from-plan` | Changed files plus verification |
| local shell/filesystem task without a failure symptom | `mac-local-ops` | Safe local action/report |

Rows for skills the repository does not ship are inert; route to the nearest shipped skill.
