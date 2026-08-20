# Severity Model

| Severity | Meaning |
|---|---|
| `BLOCKER` | Likely crash, data loss, security leak, severe data race or change that must not ship |
| `CRITICAL` | Real bug or high-risk behavior with clear reproduction path |
| `WARNING` | Maintainability or correctness risk that should be fixed soon |
| `INFO` | Low-risk observation or test gap |

Rules:

- Findings must be actionable.
- Do not report taste-only comments.
- If evidence is weak, mark it as an assumption or omit it.
- Put findings before summary.
