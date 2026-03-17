# Documentation Review Phases

## Phase 1: Inventory

Collect human-readable files: Markdown, YAML, TXT and configuration docs. Exclude `.git`, build outputs, vendor folders, binary files and lock files.

Inventory row:

```markdown
| Path | Lines | Type | Status |
|---|---:|---|---|
```

## Phase 2: Size and Structure

Apply thresholds, inspect headings, empty sections, wall-of-text and oversized sections.

## Phase 3: Duplication

Check repeated tables, lists, code blocks and paragraphs. Assign one SSOT owner per cluster.

## Phase 4: Hygiene

Check broken links, empty links, stale dates, unresolved work markers and mixed document types.

## Phase 5: Report

Save findings with severity, evidence, affected paths and exact recommendation.
