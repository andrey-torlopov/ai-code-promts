# Documentation Check Rules

## Size Thresholds

| File type | Recommended | Warning | Critical | Reason |
|---|---:|---:|---:|---|
| `SKILL.md` | 300 lines | more than 300 | more than 500 | Loaded directly by agents |
| Runtime anchor Markdown | 60 lines | more than 60 | more than 120 | Should only point to the real context |
| Router or workflow Markdown | 120 lines | more than 160 | more than 220 | Should classify, not explain everything |
| Role card | 120 lines | more than 120 | more than 220 | Role cards must stay compact |
| Generic docs | 400 lines | more than 500 | more than 700 | Scannability |
| YAML config | 200 lines | more than 300 | more than 500 | Config should not become prose |

## Structure Rules

| Rule | Severity |
|---|---|
| Skipped heading level, such as H1 to H3 | Critical |
| Broken relative link | Critical |
| Exact duplicate block longer than 5 lines | Critical |
| Anchor file copying core rules instead of linking | Warning |
| One section longer than 40 percent of the file | Warning |
| More than 20 plain-text lines without structure | Warning |
| Long line over 200 characters | Info |
| `TODO`, `FIXME`, `HACK` in docs | Info unless it blocks use |

## SSOT Rules

Every fact should have one owner. Duplicates should become links unless the file must be atomic for agent execution.

Atomic skill exception:

- A standalone skill may duplicate minimal safety rules from other skills if that is required to work without sibling folders.
- The duplicate must be short and task-specific.
- The exception never applies to `~/.claude/custom/_core/` policies: every skill may read `_core/` directly, so those are referenced, never copied.
