# Swift Patterns Index

Lazy-load by category.

Read the category summary first, then only the individual pattern file that matches the signal.
Full per-file catalog: `_index.md`.

| Category | Summary | Patterns | Use when |
|---|---|---|---|
| Common | `common/_summary.md` | `common/` | code style, naming, tests, architecture hygiene |
| Networking | `networking/_summary.md` | `networking/` | URLSession, API models, HTTP validation |
| Platform | `platform/_summary.md` | `platform/` | XCTest, async tests, retries, shared state |
| Performance | `performance/_summary.md` | `performance/` | hot paths, filesystem, string operations |
| Security | `security/_summary.md` | `security/` | PII, logging, error leakage |
| Best practices | `best-practices/_summary.md` | `best-practices/` | final classes, value types, `let` |

Protocol:

1. Identify a concrete signal.
2. Read only one category file first.
3. Quote the category and pattern in the recommendation.
4. Do not load all categories by default.
