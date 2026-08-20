# Mode: ci

Use for GitHub Actions, GitLab CI, runners, templates and pipeline logs.

## Knowledge

Load:

- `~/.claude/custom/KNOWLEDGE/devops/_rules.md`
- `~/.claude/custom/KNOWLEDGE/devops/ci-pipelines.md`
- Project-specific CI docs when present

## References

- `../references/log-analysis.md`
- `../references/ci-diagnosis.md`
- `../references/root-cause-format.md`

## Stop

Return CI root cause, evidence and pipeline fix plan. Do not deploy or mutate external CI state without a separate gate.
