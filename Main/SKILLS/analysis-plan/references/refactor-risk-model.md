# Refactoring Risk Model

| Priority | Meaning |
|---|---|
| P0 | Crash, data race, data loss or security risk |
| P1 | Architectural issue blocking development or testability |
| P2 | Maintainability debt with clear local impact |
| P3 | Low-risk cleanup or style issue |

| Risk | Criteria |
|---|---|
| High | Public API, persistence, networking, concurrency or cross-module behavior changes |
| Medium | Internal behavior change with testable impact |
| Low | Local extraction, naming, mechanical cleanup |

Each step must include dependencies and verification.
